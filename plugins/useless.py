#
# Copyright (C) 2025 by AnimeLord-Bots@Github, < https://github.com/AnimeLord-Bots >.
#
# This file is part of < https://github.com/AnimeLord-Bots/FileStore > project,
# and is released under the MIT License.
# Please see < https://github.com/AnimeLord-Bots/FileStore/blob/master/LICENSE >
#
# All rights reserved.
#

import asyncio
import os
import random
import sys
import time
from datetime import datetime, timedelta
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode, ChatAction
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, ChatInviteLink, ChatPrivileges
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserNotParticipant
from bot import Bot
from config import *
from helper_func import *
from database.database import *

#=====================================================================================##

@Bot.on_message(filters.command('stats') & admin)
async def stats(bot: Bot, message: Message):
    now = datetime.now()
    delta = now - bot.uptime
    time = get_readable_time(delta.seconds)
    await message.reply(BOT_STATS_TEXT.format(uptime=time), protect_content=get_protect_content(bot, message), disable_web_page_preview=get_hide_caption(bot, message))


#=====================================================================================##

WAIT_MSG = "<b>ᴡᴏʀᴋɪɴɢ....</b>"

#=====================================================================================##


@Bot.on_message(filters.command('users') & filters.private & admin)
async def get_users(client: Bot, message: Message):
    msg = await client.send_message(chat_id=message.chat.id, text=WAIT_MSG)
    users = await db.full_userbase()
    await msg.edit(f"{len(users)} ᴜꜱᴇʀꜱ ᴀʀᴇ ᴜꜱɪɴɢ ᴛʜɪꜱ ʙᴏᴛ", protect_content=get_protect_content(client, msg), disable_web_page_preview=get_hide_caption(client, msg))

#
# Copyright (C) 2025 by AnimeLord-Bots@Github, < https://github.com/AnimeLord-Bots >.
#
# This file is part of < https://github.com/AnimeLord-Bots/FileStore > project,
# and is released under the MIT License.
# Please see < https://github.com/AnimeLord-Bots/FileStore/blob/master/LICENSE >
#
# All rights reserved.
#

#=====================================================================================##

#AUTO-DELETE

@Bot.on_message(filters.private & filters.command('dlt_time') & admin)
async def set_delete_time(client: Bot, message: Message):
    try:
        duration = int(message.command[1])

        await db.set_del_timer(duration)

        await message.reply(f"<b>Dᴇʟᴇᴛᴇ Tɪᴍᴇʀ ʜᴀs ʙᴇᴇɴ sᴇᴛ ᴛᴏ <blockquote>{duration} sᴇᴄᴏɴᴅs.</blockquote></b>", protect_content=get_protect_content(client, message), disable_web_page_preview=get_hide_caption(client, message))

    except (IndexError, ValueError):
        await message.reply("<b>Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴠᴀʟɪᴅ ᴅᴜʀᴀᴛɪᴏɴ ɪɴ sᴇᴄᴏɴᴅs.</b> Usage: /dlt_time {duration}", protect_content=get_protect_content(client, message), disable_web_page_preview=get_hide_caption(client, message))

@Bot.on_message(filters.private & filters.command('check_dlt_time') & admin)
async def check_delete_time(client: Bot, message: Message):
    duration = await db.get_del_timer()

    await message.reply(f"<b><blockquote>Cᴜʀʀᴇɴᴛ ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇʀ ɪs sᴇᴛ ᴛᴏ {duration}sᴇᴄᴏɴᴅs.</blockquote></b>", protect_content=get_protect_content(client, message), disable_web_page_preview=get_hide_caption(client, message))

#=====================================================================================##

#
# Copyright (C) 2025 by AnimeLord-Bots@Github, < https://github.com/AnimeLord-Bots >.
#
# This file is part of < https://github.com/AnimeLord-Bots/FileStore > project,
# and is released under the MIT License.
# Please see < https://github.com/AnimeLord-Bots/FileStore/blob/master/LICENSE >
#
# All rights reserved.
#

@Bot.on_message(filters.command('fsettings') & filters.user(OWNER_ID))
async def file_settings(client: Bot, message: Message):
    user_id = message.from_user.id
    protect_content = await get_protect_content(client, message)  # Await the async function
    hide_caption = await get_hide_caption(client, message)       # Await the async function
    channel_button = await get_channel_button(client, message)   # Await the async function

    text = (
        "<b>FILES RELATED SETTINGS:</b>\n\n"
        f"> PROTECT CONTENT: {'ENABLED' if protect_content else 'DISABLED'} {'' if protect_content else '❌'}\n"
        f"> HIDE CAPTION: {'ENABLED' if hide_caption else 'DISABLED'} {'' if hide_caption else '❌'}\n"
        f"> CHANNEL BUTTON: {'ENABLED' if channel_button else 'DISABLED'} {'' if channel_button else '❌'}\n\n"
        "<b>CLICK BELOW BUTTONS TO CHANGE SETTINGS</b>"
    )

    buttons = [
        [InlineKeyboardButton("PC: ✅", callback_data="fset_pc_on" if not protect_content else "fset_pc_off"),
         InlineKeyboardButton("HC: ✅", callback_data="fset_hc_on" if not hide_caption else "fset_hc_off")],
        [InlineKeyboardButton("CB: ✅", callback_data="fset_cb_on" if not channel_button else "fset_cb_off")],
        [InlineKeyboardButton("REFRESH", callback_data="fset_refresh"),
         InlineKeyboardButton("back", callback_data="fset_back")]
    ]

    await message.reply_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=ParseMode.HTML,
        protect_content=protect_content,
        disable_web_page_preview=hide_caption
    )

@Bot.on_callback_query(filters.regex(r"^fset_"))
async def fsettings_callback(client: Bot, query: CallbackQuery):
    user_id = query.from_user.id
    action = query.data.split("_")[1]

    if action == "pc_on":
        await db.set_protect_content(user_id, True)
        await query.answer("Protect Content enabled!")
    elif action == "pc_off":
        await db.set_protect_content(user_id, False)
        await query.answer("Protect Content disabled!")
    elif action == "hc_on":
        await db.set_hide_caption(user_id, True)
        await query.answer("Hide Caption enabled!")
    elif action == "hc_off":
        await db.set_hide_caption(user_id, False)
        await query.answer("Hide Caption disabled!")
    elif action == "cb_on":
        await db.set_channel_button(user_id, True)
        await query.answer("Channel Button enabled!")
    elif action == "cb_off":
        await db.set_channel_button(user_id, False)
        await query.answer("Channel Button disabled!")
    elif action == "refresh":
        await file_settings(client, query.message)
        await query.answer("Settings refreshed!")
    elif action == "back":
        await query.message.delete()
        await query.answer("Back to menu!")

    if action in ["pc_on", "pc_off", "hc_on", "hc_off", "cb_on", "cb_off"]:
        await file_settings(client, query.message)

#
# Copyright (C) 2025 by AnimeLord-Bots@Github, < https://github.com/AnimeLord-Bots >.
#
# This file is part of < https://github.com/AnimeLord-Bots/FileStore > project,
# and is released under the MIT License.
# Please see < https://github.com/AnimeLord-Bots/FileStore/blob/master/LICENSE >
#
# All rights reserved.
