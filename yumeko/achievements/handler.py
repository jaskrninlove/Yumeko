# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
# ==========================================================

from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message

from yumeko.database.users import add_user
from yumeko.achievements.db import get_user_achievements
from yumeko.achievements.strings import achievements_text, my_badges_text


async def achievements_cmd(client, message: Message):
    user = message.from_user

    badges = []

    if user:
        await add_user(user)
        doc = await get_user_achievements(user.id)
        badges = doc.get("badges", [])

    await message.reply_text(
        achievements_text(badges),
        parse_mode=ParseMode.HTML,
        reply_to_message_id=message.id,
        disable_web_page_preview=True,
    )


async def badges_cmd(client, message: Message):
    user = message.from_user

    if not user:
        return

    await add_user(user)
    doc = await get_user_achievements(user.id)

    await message.reply_text(
        my_badges_text(user.first_name or "Player", doc.get("badges", [])),
        parse_mode=ParseMode.HTML,
        reply_to_message_id=message.id,
        disable_web_page_preview=True,
    )


def register_achievement_handlers(app):
    app.add_handler(
        MessageHandler(
            achievements_cmd,
            filters.command(["achievements", "achievement"]),
        ),
        group=200,
    )

    app.add_handler(
        MessageHandler(
            badges_cmd,
            filters.command(["badges", "mybadges"]),
        ),
        group=200,
    )