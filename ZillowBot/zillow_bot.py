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

import logging

import discord

import settings
import utils


logger = logging.getLogger('ZillowBot')


class ZillowBot(discord.Client):
    """A Discord bot that parses Zillow instant update emails
    for new listings and posts notifications with their info.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.background_task = self.loop.create_task(self.post_new_listings())

    async def on_ready(self):
        logger.info(f'Logged in as {self.user.name} with ID {self.user.id}')

    async def post_new_listings(self):
        await self.wait_until_ready()
        channel = self.get_channel(settings.DISCORD_CHANNEL)
        while not self.is_closed():
            async for listing in utils.fetch_new_listings(wait=settings.WAIT):
                logger.debug(f'Parsed new listing: {listing}')
                embed = discord.Embed(
                    title=f'A new listing at {listing.address} has appeared!',
                    description=f'Features: {listing.facts} Price: {listing.price}',
                    url=listing.url,
                )
                embed.set_image(url=listing.image_url)
                await channel.send(embed=embed)


if __name__ == '__main__':

    logging.basicConfig(format='%(asctime)s %(levelname)s [%(name)s] %(message)s', level=logging.DEBUG)

    bot = ZillowBot()
    bot.run(settings.DISCORD_TOKEN)

