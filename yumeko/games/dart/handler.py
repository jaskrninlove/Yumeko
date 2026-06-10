# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
# ==========================================================

import asyncio

from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message

from yumeko.database.users import add_user
from yumeko.games.dart.game import reward_dart
from yumeko.games.dart.strings import dart_text


async def dart_cmd(client, message: Message):
    user = message.from_user

    if not user:
        return

    await add_user(user)

    dart_msg = await client.send_dice(
        chat_id=message.chat.id,
        emoji="🎯",
        reply_to_message_id=message.id,
    )

    await asyncio.sleep(3)

    value = dart_msg.dice.value
    result = await reward_dart(user.id, value)

    await message.reply_text(
        dart_text(user.first_name or "Player", value, result),
        parse_mode=ParseMode.HTML,
        reply_to_message_id=dart_msg.id,
        disable_web_page_preview=True,
    )


def register_dart_handlers(app):
    app.add_handler(
        MessageHandler(
            dart_cmd,
            filters.command(["dart", "throw", "bullseye"]),
        ),
        group=90,
    )