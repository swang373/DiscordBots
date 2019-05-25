# MIT License
# 
# Copyright (c) 2019 Sean-Jiun Wang
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import asyncio
import collections
import email.parser
import email.policy
import imaplib
import logging
import quopri
import ssl

from bs4 import BeautifulSoup

import settings


logger = logging.getLogger('ZillowBotUtils')

email_parser = email.parser.BytesParser(policy=email.policy.default)


ZillowListing = collections.namedtuple(
    typename='ZillowListing',
    field_names=['url', 'image_url', 'price', 'facts', 'address'],
)


def parse_message_for_listing(message_data):
    """Parse a Zillow instant update email for listing information.

    Parameters
    ----------
    message_data : list
        The entire instant update email data in RFC822 format.

        This is expected to be the return value of a call to IMAP4.fetch
        which returns the lightly parsed message data as a list. The list
        contains two items:
        * The first item is a 2-tuple whose elements are the flags used by
          the FETCH command and the response containing the message, both
          of which are byte literals, respectively.
        * The second item is a byte literal containing a single closing
          parenthesis ")" appended to the end of the response.

    Returns
    -------
    listing : ZillowListing
        A namedtuple whose fields are the listing information.
    """
    message = email_parser.parsebytes(message_data[0][1])

    # Find the HTML part of the email message.
    for part in message.iter_parts():
        if part.get_content_type() == 'text/html':
            body = part.get_body()
            break

    # Decode the HTML content body from its Quoted-Printable (QP) encoding.
    body_decoded = quopri.decodestring(body.as_string())

    # Parse the HTML document tree.
    html_doc = BeautifulSoup(markup=body_decoded, features='html.parser')
    logger.debug('Dumping parsed HTML document tree...')
    logger.debug(html_doc.prettify())

    # Search the HTML document tree for listing information.
    # Sometimes the instant update email contains additional suggested
    # listings apart from the main listing which are not of interest,
    # which is why the search is limited to the first five tags with
    # aria-label attributes.
    listing_info = {}
    for tag in html_doc.find_all(attrs={'aria-label': True}, limit=5):
        aria_label = tag.get('aria-label')
        if aria_label.startswith('Property photo'):
            listing_info['url'] = tag.a.get('href')
            listing_info['image_url'] = tag.get('background')
        elif aria_label.startswith('Property price'):
            listing_info['price'] = tag.text.strip()
        elif aria_label.startswith('Property facts'):
            listing_info['facts'] = tag.text.strip()
        elif aria_label.startswith('Property address'):
            listing_info['address'] = tag.text.strip().replace(u'\u200c', '')

    listing = ZillowListing(**listing_info)

    return listing


def imap_connection(host, port, username, password):
    """Open a connection to an IMAP server."""
    ssl_context = ssl.create_default_context()
    logger.debug(f'Connecting to {host} on port {port}')
    conn = imaplib.IMAP4_SSL(host, port, ssl_context=ssl_context)
    logger.debug(f'Logging in as {username}')
    conn.login(username, password)
    return conn


async def fetch_new_listings(wait):
    """Fetch instant update emails about new listings.

    This is implemented as an asynchronous generator.

    Parameters
    ----------
    wait : numeric
        The number of seconds to wait between consecutive fetches.
    """
    with imap_connection(**settings.EMAIL_SERVICE) as conn:

        # Select the mailbox that receives instant update emails.
        response, _ = conn.select(settings.MAILBOX)
        logger.debug(f'Selecting mailbox {settings.MAILBOX}: {response}')

        # Construct the search criteria for instant update emails.
        criteria = f'(FROM "{settings.SENDER}" SUBJECT "{settings.SUBJECT}" UNSEEN)'
        logger.debug(f'Using search criteria: {criteria}')

        logger.debug(f'Fetches set to occur every {wait} seconds')
        while True:
            # Search for instant update emails.
            response, data = conn.search(None, criteria)
            msgnums = data[0].split()
            logger.info(f'Searching emails: {response}, found {len(msgnums)} messages')

            # For each instant update email found, fetch it, parse it
            # for listing information, and then mark it as seen.
            if len(msgnums) > 0:
                for msgnum in msgnums:
                    response, message_data = conn.fetch(msgnum, '(RFC822)')
                    logger.debug(f'Fetching message #{int(msgnum)}: {response}')
                    listing = parse_message_for_listing(message_data)
                    conn.store(msgnum, '+FLAGS', '\\Seen')
                    yield listing

            await asyncio.sleep(wait)

