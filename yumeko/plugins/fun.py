# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
#
#  Developer  : Jass
#  Project    : Yumeko Games Bot
#  Version    : 1.0.0
#
#  GitHub     : Private
#  License    : MIT License
#
#  This file is part of Yumeko Games Bot.
#  Unauthorized removal of this notice is discouraged.
#
#  © 2026 Jass. All Rights Reserved.
# ==========================================================

import random
import html

from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message

from yumeko.client import app
from yumeko.games.fun.interactions import ACTIONS, make_interaction_text
from yumeko.games.fun.stickers import get_stickers


FUN_COMMANDS = list(ACTIONS.keys())


def mention_user(user):
    if not user:
        return "Someone"

    name = html.escape(user.first_name or "Someone")
    return f'<a href="tg://user?id={user.id}">{name}</a>'


async def get_target(message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user

    return None


@app.on_message(filters.command(FUN_COMMANDS))
async def fun_interaction_cmd(_, message: Message):
    action = message.command[0].lower()
    user = message.from_user
    target = await get_target(message)

    if not user:
        return

    if not target:
        await message.reply_text(
            (
                f"🎭 <b>Yumeko tilts her head...</b>\n\n"
                f"Reply to someone and use <code>/{action}</code>, darling.\n\n"
                f"Example: reply to a user with <code>/{action}</code>"
            ),
            parse_mode=ParseMode.HTML,
            reply_to_message_id=message.id,
        )
        return

    bot = await app.get_me()

    user_mention = mention_user(user)
    target_mention = mention_user(target)

    mode = "normal"

    if user.id == target.id:
        mode = "self"

    if target.id == bot.id:
        mode = "bot"

    text = make_interaction_text(
        action=action,
        user=user_mention,
        target=target_mention,
        mode=mode,
    )

    stickers = get_stickers(action)

    target_message_id = message.reply_to_message.id

    if stickers:
        try:
            await app.send_sticker(
                chat_id=message.chat.id,
                sticker=random.choice(stickers),
                reply_to_message_id=target_message_id,
            )
        except Exception:
            pass

    await app.send_message(
        chat_id=message.chat.id,
        text=text,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
        reply_to_message_id=target_message_id,
    )


@app.on_message(filters.command("getid"))
async def get_file_id_cmd(_, message: Message):
    if not message.reply_to_message:
        await message.reply_text(
            "Reply to a sticker, photo, animation, video, or document with /getid.",
            reply_to_message_id=message.id,
        )
        return

    replied = message.reply_to_message

    file_id = None
    file_type = None

    if replied.sticker:
        file_id = replied.sticker.file_id
        file_type = "Sticker"
    elif replied.animation:
        file_id = replied.animation.file_id
        file_type = "Animation"
    elif replied.photo:
        file_id = replied.photo.file_id
        file_type = "Photo"
    elif replied.video:
        file_id = replied.video.file_id
        file_type = "Video"
    elif replied.document:
        file_id = replied.document.file_id
        file_type = "Document"

    if not file_id:
        await message.reply_text(
            "No supported file found in replied message.",
            reply_to_message_id=message.id,
        )
        return

    await message.reply_text(
        f"<b>{file_type} File ID:</b>\n\n<code>{file_id}</code>",
        parse_mode=ParseMode.HTML,
        reply_to_message_id=message.id,
    )