#
# Copyright (C) 2025 by AnimeLord-Bots@Github, < https://github.com/AnimeLord-Bots >.
#
# This file is part of < https://github.com/AnimeLord-Bots/FileStore > project,
# and is released under the MIT License.
# Please see < https://github.com/AnimeLord-Bots/FileStore/blob/master/LICENSE >
#
# All rights reserved.

from aiohttp import web
from plugins import web_server
import asyncio
import pyromod.listen
from pyrogram import Client
from pyrogram.enums import ParseMode
import sys
from datetime import datetime
from config import *

name = """『A N I M E _ L O R D』"""

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={
                "root": "plugins"
            },
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN
        )
        self.LOGGER = LOGGER
        self.db_channel = None  # Initialize db_channel attribute

    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        self.uptime = datetime.now()

        try:
            db_channel = await self.get_chat(CHANNEL_ID)
            self.db_channel = db_channel  # Set the db_channel instance variable
            test = await self.send_message(chat_id=db_channel.id, text="Test Message")
            await test.delete()
        except Exception as e:
            self.LOGGER(__name__).warning(f"DB channel test failed: {e}")
            self.LOGGER(__name__).warning(f"Make sure bot is admin in DB channel, and double-check CHANNEL_ID value: {CHANNEL_ID}")
            self.LOGGER(__name__).info("Bot stopped. Join https://t.me/+3lpawaYvxBU4YTY1 for support")
            sys.exit()

        self.set_parse_mode(ParseMode.HTML)  # Set parse mode once
        self.username = usr_bot_me.username
        self.LOGGER(__name__).info(f"Bot is alive..!\n\nCreated by 『Anime-Lord-Bot』")
        self.LOGGER(__name__).info(f"Bot deployed by @who-am-i")

        # Start web server
        app = web.AppRunner(await web_server())
        await app.setup()
        await web.TCPSite(app, "0.0.0.0", PORT).start()

        try:
            await self.send_message(OWNER_ID, text=f"<b><blockquote>Bot restarted by @Anime_Lord_Bot\n\n<code>{name}</code></blockquote></b>")
        except Exception as e:
            self.LOGGER(__name__).warning(f"Failed to send startup message to OWNER_ID: {str(e)}")

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped.")

    def run(self):
        """Run the bot."""
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.start())
            self.LOGGER(__name__).info(f"Bot is now alive. Thanks to @who-am-i")
            self.LOGGER(__name__).info(f"""
▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄
|------------------『A N I M E  L O R D』----------------------|
▀▄▀▄▀▄▀▄▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄
               ◈◈◈◈◈◈ ɪ_s_ᴀ_ʟ_ɪ_ᴠ_ᴇ ◈◈◈◈◈◈  
                       ▼   ᴀᴄᴄᴇssɪɴɢ   ▼  
                         ███████] 99%  
""")
            loop.run_forever()
        except KeyboardInterrupt:
            self.LOGGER(__name__).info("Bot shutdown initiated...")
        finally:
            loop.run_until_complete(self.stop())

#
# Copyright (C) 2025 by AnimeLord-Bots@Github, < https://github.com/AnimeLord-Bots >.
#
# This file is part of < https://github.com/AnimeLord-Bots/FileStore > project,
# and is released under the MIT License.
# Please see < https://github.com/AnimeLord-Bots/FileStore/blob/master/LICENSE >
#
# All rights reserved.