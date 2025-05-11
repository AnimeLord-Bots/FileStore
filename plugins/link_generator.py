#
# Copyright (C) 2025 by AnimeLord-Bots@Github, < https://github.com/AnimeLord-Bots >.
#
# This file is part of < https://github.com/AnimeLord-Bots/FileStore > project,
# and is released under the MIT License.
# Please see < https://github.com/AnimeLord-Bots/FileStore/blob/master/LICENSE >
#
# All rights reserved.
#


from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from pyrogram.enums import ParseMode
from bot import Bot
from helper_func import encode, get_message_id, admin
import re
from typing import Dict
import logging
from config import OWNER_ID
from database.database import db
from asyncio import TimeoutError

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Small caps conversion dictionary
SMALL_CAPS = {
    'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ꜰ', 'g': 'ɢ', 'h': 'ʜ',
    'i': 'ɪ', 'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ', 'o': 'ᴏ', 'p': 'ᴘ',
    'q': 'Q', 'r': 'ʀ', 's': 'ꜱ', 't': 'ᴛ', 'u': 'ᴜ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x',
    'y': 'ʏ', 'z': 'ᴢ'
}

def to_small_caps_with_html(text: str) -> str:
    """Convert text to small caps font style while preserving HTML tags."""
    result = ""
    i = 0
    while i < len(text):
        if text[i] == '<':
            # Find the closing '>' of the HTML tag
            j = i + 1
            while j < len(text) and text[j] != '>':
                j += 1
            if j < len(text):
                # Include the HTML tag as is
                result += text[i:j+1]
                i = j + 1
            else:
                # Incomplete tag, treat as normal text
                result += text[i]
                i += 1
        else:
            # Convert non-tag character to small caps
            result += SMALL_CAPS.get(text[i].lower(), text[i])
            i += 1
    return result

# Store user data for flink command
flink_user_data: Dict[int, Dict] = {}
#
# Copyright (C) 2025 by AnimeLord-Bots@Github, < https://github.com/AnimeLord-Bots >.
#
# This file is part of < https://github.com/AnimeLord-Bots/FileStore > project,
# and is released under the MIT License.
# Please see < https://github.com/AnimeLord-Bots/FileStore/blob/master/LICENSE >
#
# All rights reserved.
@Bot.on_message(filters.private & admin & filters.command('batch'))
async def batch(client: Client, message: Message):
    while True:
        try:
            first_message = await client.ask(
                text=to_small_caps_with_html("<b>━━━━━━━━━━━━━━━━━━</b>\n<blockquote><b>Forward the first message from db channel (with quotes).\nOr send the db channel post link\n</b></blockquote><b>━━━━━━━━━━━━━━━━━━</b>"),
                chat_id=message.from_user.id,
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60,
                parse_mode=ParseMode.HTML
            )
        except TimeoutError:
            print(to_small_caps_with_html(f"timeout error waiting for first message in batch command"))
            return
        f_msg_id = await get_message_id(client, first_message)
        if f_msg_id:
            break
        else:
            await first_message.reply(
                to_small_caps_with_html("<b>━━━━━━━━━━━━━━━━━━</b>\n<blockquote><b>❌ Error: This forwarded post is not from my db channel or this link is not valid.</b></blockquote>\n<b>━━━━━━━━━━━━━━━━━━</b>"),
                quote=True,
                parse_mode=ParseMode.HTML,
                protect_content=get_protect_content(client, first_message),
                disable_web_page_preview=get_hide_caption(client, first_message)
            )
            continue

    while True:
        try:
            second_message = await client.ask(
                text=to_small_caps_with_html("<b>━━━━━━━━━━━━━━━━━━</b>\n<blockquote><b>Forward the last message from db channel (with quotes).\nOr send the db channel post link\n</b></blockquote><b>━━━━━━━━━━━━━━━━━━</b>"),
                chat_id=message.from_user.id,
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60,
                parse_mode=ParseMode.HTML
            )
        except TimeoutError:
            print(to_small_caps_with_html(f"timeout error waiting for second message in batch command"))
            return
        s_msg_id = await get_message_id(client, second_message)
        if s_msg_id:
            break
        else:
            await second_message.reply(
                to_small_caps_with_html("<b>━━━━━━━━━━━━━━━━━━</b>\n<b>❌ Error: This forwarded post is not from my db channel or this link is not valid.</b>\n<b>━━━━━━━━━━━━━━━━━━</b>"),
                quote=True,
                parse_mode=ParseMode.HTML,
                protect_content=get_protect_content(client, second_message),
                disable_web_page_preview=get_hide_caption(client, second_message)
            )
            continue

    string = f"get-{f_msg_id * abs(client.db_channel.id)}-{s_msg_id * abs(client.db_channel.id)}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]]) if not get_channel_button(client, second_message) else None
    await second_message.reply_text(
        to_small_caps_with_html(f"<b>━━━━━━━━━━━━━━━━━━</b>\n<blockquote><b>Here is your link:</b></blockquote>\n\n{link}\n<b>━━━━━━━━━━━━━━━━━━</b>"),
        quote=True,
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML,
        protect_content=get_protect_content(client, second_message),
        disable_web_page_preview=get_hide_caption(client, second_message)
    )
#
# Copyright (C) 2025 by AnimeLord-Bots@Github, < https://github.com/AnimeLord-Bots >.
#
# This file is part of < https://github.com/AnimeLord-Bots/FileStore > project,
# and is released under the MIT License.
# Please see < https://github.com/AnimeLord-Bots/FileStore/blob/master/LICENSE >
#
# All rights reserved.
@Bot.on_message(filters.private & admin & filters.command('genlink'))
async def link_generator(client: Client, message: Message):
    while True:
        try:
            channel_message = await client.ask(
                text=to_small_caps_with_html("<b>━━━━━━━━━━━━━━━━━━</b>\n<blockquote><b>Forward message from the db channel (with quotes).\nOr send the db channel post link\n</b></blockquote><b>━━━━━━━━━━━━━━━━━━</b>"),
                chat_id=message.from_user.id,
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60,
                parse_mode=ParseMode.HTML
            )
        except TimeoutError:
            print(to_small_caps_with_html(f"timeout error waiting for message in genlink command"))
            return
        msg_id = await get_message_id(client, channel_message)
        if msg_id:
            break
        else:
            await channel_message.reply(
                to_small_caps_with_html("<b>━━━━━━━━━━━━━━━━━━</b>\n<blockquote><b>❌ Error: This forwarded post is not from my db channel or this link is not valid.</b></blockquote>\n<b>━━━━━━━━━━━━━━━━━━</b>"),
                quote=True,
                parse_mode=ParseMode.HTML,
                protect_content=get_protect_content(client, channel_message),
                disable_web_page_preview=get_hide_caption(client, channel_message)
            )
            continue

    base64_string = await encode(f"get-{msg_id * abs(client.db_channel.id)}")
    link = f"https://t.me/{client.username}?start={base64_string}"
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]]) if not get_channel_button(client, channel_message) else None
    await channel_message.reply_text(
        to_small_caps_with_html(f"<b>━━━━━━━━━━━━━━━━━━</b>\n<blockquote><b>Here is your link:</b></blockquote>\n\n{link}\n<b>━━━━━━━━━━━━━━━━━━</b>"),
        quote=True,
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML,
        protect_content=get_protect_content(client, channel_message),
        disable_web_page_preview=get_hide_caption(client, channel_message)
    )
#
# Copyright (C) 2025 by AnimeLord-Bots@Github, < https://github.com/AnimeLord-Bots >.
#
# This file is part of < https://github.com/AnimeLord-Bots/FileStore > project,
# and is released under the MIT License.
# Please see < https://github.com/AnimeLord-Bots/FileStore/blob/master/LICENSE >
#
# All rights reserved.
@Bot.on_message(filters.private & admin & filters.command("custom_batch"))
async def custom_batch(client: Client, message: Message):
    collected = []
    STOP_KEYBOARD = ReplyKeyboardMarkup([["stop"]], resize_keyboard=True)

    await message.reply(
        to_small_caps_with_html("<b>━━━━━━━━━━━━━━━━━━</b>\n<blockquote><b>Send all messages you want to include in batch.\n\nPress Stop when you're done.</b></blockquote>\n<b>━━━━━━━━━━━━━━━━━━</b>"),
        reply_markup=STOP_KEYBOARD,
        parse_mode=ParseMode.HTML,
        protect_content=get_protect_content(client, message),
        disable_web_page_preview=get_hide_caption(client, message)
    )

    while True:
        try:
            user_msg = await client.ask(
                chat_id=message.chat.id,
                text=to_small_caps_with_html("<b>━━━━━━━━━━━━━━━━━━</b>\n<blockquote><b>Waiting for files/messages...\nPress Stop to finish.</b></blockquote>\n<b>━━━━━━━━━━━━━━━━━━</b>"),
                timeout=60,
                parse_mode=ParseMode.HTML
            )
        except TimeoutError:
            print(to_small_caps_with_html(f"timeout error waiting for message in custom_batch command"))
            break

        if user_msg.text and user_msg.text.strip().lower() == "stop":
            break

        try:
            sent = await user_msg.copy(client.db_channel.id, disable_notification=True)
            collected.append(sent.id)
        except Exception as e:
            await message.reply(to_small_caps_with_html(f"<b>━━━━━━━━━━━━━━━━━━</b>\n<blockquote><b>❌ Failed to store a message:</b></blockquote>\n<code>{e}</code>\n<b>━━━━━━━━━━━━━━━━━━</b>"), parse_mode=ParseMode.HTML,
                protect_content=get_protect_content(client, message),
                disable_web_page_preview=get_hide_caption(client, message))
            print(to_small_caps_with_html(f"error storing message in custom_batch: {e}"))
            continue

    await message.reply(to_small_caps_with_html("<b>━━━━━━━━━━━━━━━━━━</b>\n<blockquote><b>✅ Batch collection complete.</b></blockquote>\n<b>━━━━━━━━━━━━━━━━━━</b>"), reply_markup=ReplyKeyboardRemove(), parse_mode=ParseMode.HTML,
        protect_content=get_protect_content(client, message),
        disable_web_page_preview=get_hide_caption(client, message))

    if not collected:
        await message.reply(to_small_caps_with_html("<b>━━━━━━━━━━━━━━━━━━</b>\n<b>❌ No messages were added to batch.</b>\n<b>━━━━━━━━━━━━━━━━━━</b>"), parse_mode=ParseMode.HTML,
            protect_content=get_protect_content(client, message),
            disable_web_page_preview=get_hide_caption(client, message))
        return

    start_id = collected[0] * abs(client.db_channel.id)
    end_id = collected[-1] * abs(client.db_channel.id)
    string = f"get-{start_id}-{end_id}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]]) if not get_channel_button(client, message) else None
    await message.reply(
        to_small_caps_with_html(f"<b>━━━━━━━━━━━━━━━━━━</b>\n<blockquote><b>Here is your custom batch link:</b></blockquote>\n\n{link}\n<b>━━━━━━━━━━━━━━━━━━</b>"),
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML,
        protect_content=get_protect_content(client, message),
        disable_web_page_preview=get_hide_caption(client, message)
    )
#
# Copyright (C) 2025 by AnimeLord-Bots@Github, < https://github.com/AnimeLord-Bots >.
#
# This file is part of < https://github.com/AnimeLord-Bots/FileStore > project,
# and is released under the MIT License.
# Please see < https://github.com/AnimeLord-Bots/FileStore/blob/master/LICENSE >
#
# All rights reserved.
@Bot.on_message(filters.private & admin & filters.command('flink'))
async def flink_command(client: Client, message: Message):
    logger.info(to_small_caps_with_html(f"flink command triggered by user {message.from_user.id}"))
    try:
        # Check if user is owner or admin
        admin_ids = await db.get_all_admins() or []
        if message.from_user.id not in admin_ids and message.from_user.id != OWNER_ID:
            await message.reply_text(to_small_caps_with_html("<b>━━━━━━━━━━━━━━━━━━</b>\n<b>❌ You are not authorized!</b>\n<b>━━━━━━━━━━━━━━━━━━</b>"), parse_mode=ParseMode.HTML,
                protect_content=get_protect_content(client, message),
                disable_web_page_preview=get_hide_caption(client, message))
            return

        # Initialize user data
        flink_user_data[message.from_user.id] = {
            'format': None,
            'links': {},
            'edit_data': {},
            'menu_message': None,
            'output_message': None,
            'caption_prompt_message': None,
            'awaiting_format': False,
            'awaiting_caption': False,
            'awaiting_db_post': False
        }
        
        await show_flink_main_menu(client, message)
    except Exception as e:
        logger.error(to_small_caps_with_html(f"error in flink_command: {e}"))
        await message.reply_text(to_small_caps_with_html("<b>━━━━━━━━━━━━━━━━━━</b>\n<b>❌ An error occurred. Please try again.</b>\n<b>━━━━━━━━━━━━━━━━━━</b>"), parse_mode=ParseMode.HTML,
            protect_content=get_protect_content(client, message),
            disable_web_page_preview=get_hide_caption(client, message))

async def show_flink_main_menu(client: Client, message: Message, edit: bool = False):
    try:
        current_format = flink_user_data[message.from_user.id]['format'] or "Not set"
        text = to_small_caps_with_html(f"<b>━━━━━━━━━━━━━━━━━━</b>\n<b>Formatted Link Generator</b>\n\n<blockquote><b>Current format:</b></blockquote>\n<blockquote><code>{current_format}</code></blockquote>\n<b>━━━━━━━━━━━━━━━━━━</b>")
        
        buttons = [
            [
                InlineKeyboardButton("• sᴇᴛ ғᴏʀᴍᴀᴛ •", callback_data="flink_set_format"),
                InlineKeyboardButton("• sᴛᴀʀᴛ ᴘʀᴏᴄᴇss •", callback_data="flink_start_process")
            ],
            [
                InlineKeyboardButton("• ʀᴇғʀᴇsʜ •", callback_data="flink_refresh"),
                InlineKeyboardButton("• ᴄʟᴏsᴇ •", callback_data="flink_close")
            ]
        ]
        
        if edit:
            if message.text != text or message.reply_markup != InlineKeyboardMarkup(buttons):
                msg = await message.edit_text(
                    text=text,
                    reply_markup=InlineKeyboardMarkup(buttons),
                    parse_mode=ParseMode.HTML
                )
                flink_user_data[message.from_user.id]['menu_message'] = msg
            else:
                logger.info(to_small_caps_with_html(f"skipping edit in show_flink_main_menu for user {message.from_user.id} - content unchanged"))
        else:
            msg = await message.reply(
                text=text,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.HTML,
                protect_content=get_protect_content(client, message),
                disable_web_page_preview=get_hide_caption(client, message)
            )
            flink_user_data[message.from_user.id]['menu_message'] = msg
    except Exception as e:
        logger.error(to_small_caps_with_html(f"error in show_flink_main_menu: {e}"))
        await message.reply_text(to_small_caps_with_html("<b>━━━━━━━━━━━━━━━━━━</b>\n<b>❌ An error occurred while showing menu.</b>\n<b>━━━━━━━━━━━━━━━━━━</b>"), parse_mode=ParseMode.HTML,
            protect_content=get_protect_content(client, message),
            disable_web_page_preview=get_hide_caption(client, message))
#
# Copyright (C) 2025 by AnimeLord-Bots@Github, < https://github.com/AnimeLord-Bots >.
#
# This file is part of < https://github.com/AnimeLord-Bots/FileStore > project,
# and is released under the MIT License.
# Please see < https://github.com/AnimeLord-Bots/FileStore/blob/master/LICENSE >
#
# All rights reserved.
@Bot.on_callback_query(filters.regex(r"^flink_set_format$"))
async def flink_set_format_callback(client: Client, query: CallbackQuery):
    logger.info(to_small_caps_with_html(f"flink_set_format callback triggered by user {query.from_user.id}"))
    try:
        admin_ids = await db.get_all_admins() or []
        if query.from_user.id not in admin_ids and query.from_user.id != OWNER_ID:
            await query.answer(to_small_caps_with_html("You are not authorized!"), show_alert=True)
            return

        flink_user_data[query.from_user.id]['awaiting_format'] = True
        current_text = query.message.text if query.message.text else ""
        new_text = to_small_caps_with_html(
            "<b>━━━━━━━━━━━━━━━━━━</b>\n"
            "<blockquote><b>Please send your format in this pattern:</b></blockquote>\n\n"
            "<blockquote>Example</blockquote>:\n\n"
            "<blockquote>don't copy this. please type</blockquote>:\n"
            "<blockquote><code>360p = 2, 720p = 2, 1080p = 2, 4k = 2, HDRIP = 2</code></blockquote>\n\n"
            "<blockquote><b>Meaning:</b></blockquote>\n"
            "<b>- 360p = 2 → 2 video files for 360p quality</b>\n"
            "<blockquote><b>- If stickers/gifs follow, they will be included in the link\n"
            "- Only these qualities will be created</b></blockquote>\n\n"
            "<b>Send the format in the next message (no need to reply).</b>\n"
            "<b>━━━━━━━━━━━━━━━━━━</b>"
        )
        
        if current_text != new_text:
            await query.message.edit_text(
                text=new_text,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back", callback_data="flink_back_to_menu")]
                ]),
                parse_mode=ParseMode.HTML
            )
        else:
            logger.info(to_small_caps_with_html(f"skipping edit in flink_set_format_callback for user {query.from_user.id} - content unchanged"))
        
        await query.answer(to_small_caps_with_html("Enter format"))
    except Exception as e:
        logger.error(to_small_caps_with_html(f"error in flink_set_format_callback: {e}"))
        await query.message.edit_text(to_small_caps_with_html("<b>━━━━━━━━━━━━━━━━━━</b>\n<b>❌ An error occurred while setting format.</b>\n<b>━━━━━━━━━━━━━━━━━━</b>"), parse_mode=ParseMode.HTML)
#
# Copyright (C) 2025 by AnimeLord-Bots@Github, < https://github.com/AnimeLord-Bots >.
#
# This file is part of < https://github.com/AnimeLord-Bots/FileStore > project,
# and is released under the MIT License.
# Please see < https://github.com/AnimeLord-Bots/FileStore/blob/master/LICENSE >
#
# All rights reserved.
@Bot.on_message(filters.private & filters.text & filters.regex(r"^[a-zA-Z0-9]+\s*=\s*\d+(,\s*[a-zA-Z0-9]+\s*=\s*\d+)*$"))
async def handle_format_input(client: Client, message: Message):
    logger.info(to_small_caps_with_html(f"format input received from user {message.from_user.id}"))
    try:
        admin_ids = await db.get_all_admins() or []
        if message.from_user.id not in admin_ids and message.from_user.id != OWNER_ID:
            await message.reply_text(to_small_caps_with_html("<b>━━━━━━━━━━━━━━━━━━</b>\n<b>❌ You are not authorized!</b>\n<b>━━━━━━━━━━━━━━━━━━</b>"), parse_mode=ParseMode.HTML,
                protect_content=get_protect_content(client, message),
                disable_web_page_preview=get_hide_caption(client, message))
            return

        user_id = message.from_user.id
        if user_id in flink_user_data and flink_user_data[user_id].get('awaiting_format'):
            format_text = message.text.strip()
            flink_user_data[user_id]['format'] = format_text
            flink_user_data[user_id]['awaiting_format'] = False
            await message.reply_text(to_small_caps_with_html(f"<b>━━━━━━━━━━━━━━━━━━</b>\n<blockquote><b>✅ Format saved successfully:</b></blockquote>\n<code>{format_text}</code>\n<b>━━━━━━━━━━━━━━━━━━</b>"), parse_mode=ParseMode.HTML,
                protect_content=get_protect_content(client, message),
                disable_web_page_preview=get_hide_caption(client, message))
            await show_flink_main_menu(client, message)
        else:
            logger.info(to_small_caps_with_html(f"format input ignored for user {message.from_user.id} - not awaiting format"))
            await message.reply_text(
                to_small_caps_with_html("<b>━━━━━━━━━━━━━━━━━━</b>\n<blockquote><b>❌ Please use the 'Set Format' option first and provide a valid format</b></blockquote>\n<blockquote>Example:</blockquote> <code>360p = 2, 720p = 1</code>\n<b>━━━━━━━━━━━━━━━━━━</b>"),
                parse_mode=ParseMode.HTML,
                protect_content=get_protect_content(client, message),
                disable_web_page_preview=get_hide_caption(client, message)
            )
    except Exception as e:
        logger.error(to_small_caps_with_html(f"error in handle_format_input: {e}"))
        await message.reply_text(to_small_caps_with_html("<b>━━━━━━━━━━━━━━━━━━</b>\n<b>❌ An error occurred while processing format.</b>\n<b>━━━━━━━━━━━━━━━━━━</b>"), parse_mode=ParseMode.HTML,
            protect_content=get_protect_content(client, message),
            disable_web_page_preview=get_hide_caption(client, message))
#
# Copyright (C) 2025 by AnimeLord-Bots@Github, < https://github.com/AnimeLord-Bots >.
#
# This file is part of < https://github.com/AnimeLord-Bots/FileStore > project,
# and is released under the MIT License.
# Please see < https://github.com/AnimeLord-Bots/FileStore/blob/master/LICENSE >
#
# All rights reserved.
@Bot.on_callback_query(filters.regex(r"^flink_start_process$"))
async def flink_start_process_callback(client: Client, query: CallbackQuery):
    logger.info(to_small_caps_with_html(f"flink_start_process callback triggered by user {query.from_user.id}"))
    try:
        admin_ids = await db.get_all_admins() or []
        if query.from_user.id not in admin_ids and query.from_user.id != OWNER_ID:
            await query.answer(to_small_caps_with_html("You are not authorized!"), show_alert=True)
            return

        if not flink_user_data[query.from_user.id]['format']:
            await query.answer(to_small_caps_with_html("Please set a format first!"), show_alert=True)
            return

        flink_user_data[query.from_user.id]['awaiting_db_post'] = True
        await query.message.edit_text(
            to_small_caps_with_html("<b>━━━━━━━━━━━━━━━━━━</b>\n<blockquote><b>Please forward the DB channel post or send its link to generate formatted links.</b></blockquote>\n<b>━━━━━━━━━━━━━━━━━━</b>"),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="flink_back_to_menu")]
            ]),
            parse_mode=ParseMode.HTML
        )
        await query.answer(to_small_caps_with_html("Forward DB post now"))
    except Exception as e:
        logger.error(to_small_caps_with_html(f"error in flink_start_process_callback: {e}"))
        await query.message.edit_text(to_small_caps_with_html("<b>━━━━━━━━━━━━━━━━━━</b>\n<b>❌ An error occurred while starting process.</b>\n<b>━━━━━━━━━━━━━━━━━━</b>"), parse_mode=ParseMode.HTML)
#
# Copyright (C) 2025 by AnimeLord-Bots@Github, < https://github.com/AnimeLord-Bots >.
#
# This file is part of < https://github.com/AnimeLord-Bots/FileStore > project,
# and is released under the MIT License.
# Please see < https://github.com/AnimeLord-Bots/FileStore/blob/master/LICENSE >
#
# All rights reserved.
@Bot.on_message(filters.private & (filters.forwarded | (filters.text & ~filters.forwarded)) & filters.create(lambda _, __, m: m.from_user.id in flink_user_data and flink_user_data[m.from_user.id].get('awaiting_db_post')))
async def handle_db_post_input(client: Client, message: Message):
    logger.info(to_small_caps_with_html(f"DB post input received from user {message.from_user.id}"))
    try:
        admin_ids = await db.get_all_admins() or []
        if message.from_user.id not in admin_ids and message.from_user.id != OWNER_ID:
            await message.reply_text(to_small_caps_with_html("<b>━━━━━━━━━━━━━━━━━━</b>\n<b>❌ You are not authorized!</b>\n<b>━━━━━━━━━━━━━━━━━━</b>"), parse_mode=ParseMode.HTML,
                protect_content=get_protect_content(client, message),
                disable_web_page_preview=get_hide_caption(client, message))
            return

        user_id = message.from_user.id
        if user_id not in flink_user_data or not flink_user_data[user_id].get('awaiting_db_post'):
            logger.info(to_small_caps_with_html(f"DB post input ignored for user {message.from_user.id} - not awaiting DB post"))
            return

        msg_id = await get_message_id(client, message)
        if not msg_id:
            await message.reply(
                to_small_caps_with_html("<b>━━━━━━━━━━━━━━━━━━</b>\n<blockquote><b>❌ Error: This forwarded post is not from my DB channel or this link is not valid.</b></blockquote>\n<b>━━━━━━━━━━━━━━━━━━</b>"),
                quote=True,
                parse_mode=ParseMode.HTML,
                protect_content=get_protect_content(client, message),
                disable_web_page_preview=get_hide_caption(client, message)
            )
            return

        flink_user_data[user_id]['awaiting_db_post'] = False
        base64_string = await encode(f"get-{msg_id * abs(client.db_channel.id)}")
        link = f"https://t.me/{client.username}?start={base64_string}"
        flink_user_data[user_id]['links'][msg_id] = link

        format_text = flink_user_data[user_id]['format']
        formats = dict(item.split('=') for item in format_text.split(','))
        links_text = ""
        for quality, count in formats.items():
            quality = quality.strip()
            count = int(count.strip())
            for i in range(count):
                links_text += f"{quality} Link {i+1}: {link}\n"

        await message.reply_text(
            to_small_caps_with_html(f"<b>━━━━━━━━━━━━━━━━━━</b>\n<blockquote><b>Generated Links:</b></blockquote>\n\n{links_text}\n<b>━━━━━━━━━━━━━━━━━━</b>"),
            quote=True,
            parse_mode=ParseMode.HTML,
            protect_content=get_protect_content(client, message),
            disable_web_page_preview=get_hide_caption(client, message)
        )

        flink_user_data[user_id]['output_message'] = await message.reply_text(
            to_small_caps_with_html("<b>━━━━━━━━━━━━━━━━━━</b>\n<blockquote><b>Would you like to add a custom caption? (Yes/No)</b></blockquote>\n<b>━━━━━━━━━━━━━━━━━━</b>"),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Yes", callback_data="flink_add_caption"),
                 InlineKeyboardButton("No", callback_data="flink_no_caption")]
            ]),
            parse_mode=ParseMode.HTML,
            protect_content=get_protect_content(client, message),
            disable_web_page_preview=get_hide_caption(client, message)
        )
    except Exception as e:
        logger.error(to_small_caps_with_html(f"error in handle_db_post_input: {e}"))
        await message.reply_text(to_small_caps_with_html("<b>━━━━━━━━━━━━━━━━━━</b>\n<b>❌ An error occurred while processing DB post.</b>\n<b>━━━━━━━━━━━━━━━━━━</b>"), parse_mode=ParseMode.HTML,
            protect_content=get_protect_content(client, message),
            disable_web_page_preview=get_hide_caption(client, message))
#
# Copyright (C) 2025 by AnimeLord-Bots@Github, < https://github.com/AnimeLord-Bots >.
#
# This file is part of < https://github.com/AnimeLord-Bots/FileStore > project,
# and is released under the MIT License.
# Please see < https://github.com/AnimeLord-Bots/FileStore/blob/master/LICENSE >
#
# All rights reserved.
@Bot.on_callback_query(filters.regex(r"^(flink_add_caption|flink_no_caption)$"))
async def handle_caption_choice(client: Client, query: CallbackQuery):
    logger.info(to_small_caps_with_html(f"caption choice callback triggered by user {query.from_user.id}"))
    try:
        admin_ids = await db.get_all_admins() or []
        if query.from_user.id not in admin_ids and query.from_user.id != OWNER_ID:
            await query.answer(to_small_caps_with_html("You are not authorized!"), show_alert=True)
            return

        user_id = query.from_user.id
        if user_id not in flink_user_data:
            await query.answer(to_small_caps_with_html("Session expired! Please start again."), show_alert=True)
            return

        if query.data == "flink_add_caption":
            flink_user_data[user_id]['awaiting_caption'] = True
            await query.message.edit_text(
                to_small_caps_with_html("<b>━━━━━━━━━━━━━━━━━━</b>\n<blockquote><b>Please send your custom caption now.</b></blockquote>\n<b>━━━━━━━━━━━━━━━━━━</b>"),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back", callback_data="flink_back_to_menu")]
                ]),
                parse_mode=ParseMode.HTML
            )
            await query.answer(to_small_caps_with_html("Send your caption"))
        else:  # flink_no_caption
            await query.message.delete()
            await show_flink_main_menu(client, query.message)
            await query.answer(to_small_caps_with_html("Caption skipped"))
    except Exception as e:
        logger.error(to_small_caps_with_html(f"error in handle_caption_choice: {e}"))
        await query.message.edit_text(to_small_caps_with_html("<b>━━━━━━━━━━━━━━━━━━</b>\n<b>❌ An error occurred while handling caption choice.</b>\n<b>━━━━━━━━━━━━━━━━━━</b>"), parse_mode=ParseMode.HTML)
#
# Copyright (C) 2025 by AnimeLord-Bots@Github, < https://github.com/AnimeLord-Bots >.
#
# This file is part of < https://github.com/AnimeLord-Bots/FileStore > project,
# and is released under the MIT License.
# Please see < https://github.com/AnimeLord-Bots/FileStore/blob/master/LICENSE >
#
# All rights reserved.
@Bot.on_message(filters.private & filters.text & filters.create(lambda _, __, m: m.from_user.id in flink_user_data and flink_user_data[m.from_user.id].get('awaiting_caption')))
async def handle_caption_input(client: Client, message: Message):
    logger.info(to_small_caps_with_html(f"caption input received from user {message.from_user.id}"))
    try:
        admin_ids = await db.get_all_admins() or []
        if message.from_user.id not in admin_ids and message.from_user.id != OWNER_ID:
            await message.reply_text(to_small_caps_with_html("<b>━━━━━━━━━━━━━━━━━━</b>\n<b>❌ You are not authorized!</b>\n<b>━━━━━━━━━━━━━━━━━━</b>"), parse_mode=ParseMode.HTML,
                protect_content=get_protect_content(client, message),
                disable_web_page_preview=get_hide_caption(client, message))
            return

        user_id = message.from_user.id
        if user_id not in flink_user_data or not flink_user_data[user_id].get('awaiting_caption'):
            logger.info(to_small_caps_with_html(f"caption input ignored for user {message.from_user.id} - not awaiting caption"))
            return

        flink_user_data[user_id]['awaiting_caption'] = False
        caption = message.text.strip()
        flink_user_data[user_id]['edit_data']['caption'] = caption

        links_text = ""
        for msg_id, link in flink_user_data[user_id]['links'].items():
            links_text += f"{link}\n{caption}\n\n" if caption else f"{link}\n\n"

        await message.reply_text(
            to_small_caps_with_html(f"<b>━━━━━━━━━━━━━━━━━━</b>\n<blockquote><b>Updated Links with Caption:</b></blockquote>\n\n{links_text}\n<b>━━━━━━━━━━━━━━━━━━</b>"),
            quote=True,
            parse_mode=ParseMode.HTML,
            protect_content=get_protect_content(client, message),
            disable_web_page_preview=get_hide_caption(client, message)
        )

        await show_flink_main_menu(client, message)
    except Exception as e:
        logger.error(to_small_caps_with_html(f"error in handle_caption_input: {e}"))
        await message.reply_text(to_small_caps_with_html("<b>━━━━━━━━━━━━━━━━━━</b>\n<b>❌ An error occurred while processing caption.</b>\n<b>━━━━━━━━━━━━━━━━━━</b>"), parse_mode=ParseMode.HTML,
            protect_content=get_protect_content(client, message),
            disable_web_page_preview=get_hide_caption(client, message))
#
# Copyright (C) 2025 by AnimeLord-Bots@Github, < https://github.com/AnimeLord-Bots >.
#
# This file is part of < https://github.com/AnimeLord-Bots/FileStore > project,
# and is released under the MIT License.
# Please see < https://github.com/AnimeLord-Bots/FileStore/blob/master/LICENSE >
#
# All rights reserved.
@Bot.on_callback_query(filters.regex(r"^(flink_refresh|flink_close|flink_back_to_menu)$"))
async def handle_menu_actions(client: Client, query: CallbackQuery):
    logger.info(to_small_caps_with_html(f"menu action callback triggered by user {query.from_user.id}: {query.data}"))
    try:
        admin_ids = await db.get_all_admins() or []
        if query.from_user.id not in admin_ids and query.from_user.id != OWNER_ID:
            await query.answer(to_small_caps_with_html("You are not authorized!"), show_alert=True)
            return

        user_id = query.from_user.id
        if user_id not in flink_user_data:
            await query.answer(to_small_caps_with_html("Session expired! Please start again."), show_alert=True)
            return

        if query.data == "flink_refresh":
            await show_flink_main_menu(client, query.message, edit=True)
            await query.answer(to_small_caps_with_html("Refreshed"))
        elif query.data == "flink_close":
            await query.message.delete()
            if user_id in flink_user_data:
                del flink_user_data[user_id]
            await query.answer(to_small_caps_with_html("Closed"))
        elif query.data == "flink_back_to_menu":
            await show_flink_main_menu(client, query.message, edit=True)
            await query.answer(to_small_caps_with_html("Back to menu"))
    except Exception as e:
        logger.error(to_small_caps_with_html(f"error in handle_menu_actions: {e}"))
        await query.message.edit_text(to_small_caps_with_html("<b>━━━━━━━━━━━━━━━━━━</b>\n<b>❌ An error occurred while handling menu action.</b>\n<b>━━━━━━━━━━━━━━━━━━</b>"), parse_mode=ParseMode.HTML)

#
# Copyright (C) 2025 by AnimeLord-Bots@Github, < https://github.com/AnimeLord-Bots >.
#
# This file is part of < https://github.com/AnimeLord-Bots/FileStore > project,
# and is released under the MIT License.
# Please see < https://github.com/AnimeLord-Bots/FileStore/blob/master/LICENSE >
#
# All rights reserved.