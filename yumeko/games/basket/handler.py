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
from yumeko.games.basket.game import reward_basket
from yumeko.games.basket.strings import basket_text


async def basket_cmd(client, message: Message):
    user = message.from_user

    if not user:
        return

    await add_user(user)

    basket_msg = await client.send_dice(
        chat_id=message.chat.id,
        emoji="🏀",
        reply_to_message_id=message.id,
    )

    await asyncio.sleep(3)

    value = basket_msg.dice.value
    result = await reward_basket(user.id, value)

    await message.reply_text(
        basket_text(user.first_name or "Player", value, result),
        parse_mode=ParseMode.HTML,
        reply_to_message_id=basket_msg.id,
        disable_web_page_preview=True,
    )


def register_basket_handlers(app):
    app.add_handler(
        MessageHandler(
            basket_cmd,
            filters.command(["basket", "basketball", "hoop"]),
        ),
        group=100,
    )