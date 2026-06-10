# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
# ==========================================================

from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message

from yumeko.database.users import add_user
from yumeko.games.toss.game import flip_coin, normalize_guess, reward_toss
from yumeko.games.toss.strings import toss_text, usage_text


async def toss_cmd(client, message: Message):
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

    result = flip_coin()
    won = guess == result if guess else False

    await reward_toss(user.id, guessed=guess is not None, won=won)

    await message.reply_text(
        toss_text(user.first_name or "Player", result, guess),
        parse_mode=ParseMode.HTML,
        reply_to_message_id=message.id,
        disable_web_page_preview=True,
    )


def register_toss_handlers(app):
    app.add_handler(
        MessageHandler(
            toss_cmd,
            filters.command(["toss", "coinflip", "flip"]),
        ),
        group=60,
    )