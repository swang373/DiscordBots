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

"""
The configuration for a Discord bot that fetches Zillow instant update emails
for new listings and posts their information to a text channel. Treat this as
a template or suggestion for the configuration you use in production.
"""

# Email Service
#
# The configuration options for the email service you
# used to subscribe to Zillow instant updates.
EMAIL_SERVICE = {
    # The name and port number of the host server.
    'host': 'imap.youremailprovider.com',
    'port': 993,
    # The username and password for your email account.
    # WARNING: Please scrub ALL sensitive information
    # from this file before committing it to a repo!
    'username': 'username@youremailprovider.com',
    'password': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
}

# Search Criteria
#
# The sender and subject used to search for instant update
# emails in a specific mailbox.
MAILBOX = 'INBOX'
SENDER = 'rental-instant-updates@mail.zillow.com'
SUBJECT = 'New Listing'

# Discord Bot
#
# The bot token and the ID of the text channel where it is
# allowed to post new listings.
DISCORD_TOKEN = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX' 
DISCORD_CHANNEL = 000000000000000000

