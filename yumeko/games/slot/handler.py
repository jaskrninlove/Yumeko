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
from yumeko.games.slot.game import reward_slot
from yumeko.games.slot.strings import slot_text


async def slot_cmd(client, message: Message):
    user = message.from_user

    if not user:
        return

    await add_user(user)

    dice_msg = await client.send_dice(
        chat_id=message.chat.id,
        emoji="🎰",
        reply_to_message_id=message.id,
    )

    await asyncio.sleep(3)

    value = dice_msg.dice.value
    result = await reward_slot(user.id, value)

    await message.reply_text(
        slot_text(user.first_name or "Player", value, result),
        parse_mode=ParseMode.HTML,
        reply_to_message_id=dice_msg.id,
        disable_web_page_preview=True,
    )


def register_slot_handlers(app):
    app.add_handler(
        MessageHandler(
            slot_cmd,
            filters.command(["slot", "spin", "slots"]),
        ),
        group=80,
    )