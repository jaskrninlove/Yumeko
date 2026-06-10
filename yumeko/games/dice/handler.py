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
from yumeko.games.dice.game import normalize_guess, reward_dice
from yumeko.games.dice.strings import dice_text, usage_text


async def dice_cmd(client, message: Message):
    user = message.from_user

    if not user:
        return

    await add_user(user)

    guess = None

    if len(message.command) > 1:
        guess = normalize_guess(message.command[1])

        if guess is None:
            await message.reply_text(
                usage_text(),
                parse_mode=ParseMode.HTML,
                reply_to_message_id=message.id,
            )
            return

    dice_msg = await client.send_dice(
        chat_id=message.chat.id,
        emoji="🎲",
        reply_to_message_id=message.id,
    )

    await asyncio.sleep(3)

    result = dice_msg.dice.value
    won = guess == result if guess is not None else False

    await reward_dice(user.id, guessed=guess is not None, won=won)

    await message.reply_text(
        dice_text(user.first_name or "Player", result, guess),
        parse_mode=ParseMode.HTML,
        reply_to_message_id=dice_msg.id,
        disable_web_page_preview=True,
    )


def register_dice_handlers(app):
    app.add_handler(
        MessageHandler(
            dice_cmd,
            filters.command(["dice", "roll"]),
        ),
        group=70,
    )