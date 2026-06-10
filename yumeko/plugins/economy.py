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

from pyrogram import filters
from pyrogram.types import Message

from yumeko.client import app
from yumeko.database.users import add_user
from yumeko.database.economy import claim_daily
from yumeko.helpers.buttons import back_home_buttons
from yumeko.locales import get_text


@app.on_message(filters.command("daily"))
async def daily_cmd(_, message: Message):
    user = message.from_user

    await add_user(user)

    result = await claim_daily(user.id)

    if result["success"]:
        await message.reply_text(
            get_text(
                "daily_success",
                coins=result["coins"],
                xp=result["xp"],
            ),
            reply_markup=back_home_buttons(),
            disable_web_page_preview=True,
        )
        return

    if result["reason"] == "cooldown":
        await message.reply_text(
            get_text(
                "daily_cooldown",
                hours=result["hours"],
                minutes=result["minutes"],
                seconds=result["seconds"],
            ),
            reply_markup=back_home_buttons(),
            disable_web_page_preview=True,
        )
        return

    await message.reply_text(
        get_text("daily_user_not_found"),
        reply_markup=back_home_buttons(),
        disable_web_page_preview=True,
    )