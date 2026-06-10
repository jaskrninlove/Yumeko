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
from yumeko.database.stats import get_global_stats
from yumeko.helpers.buttons import back_home_buttons
from yumeko.locales import get_text


@app.on_message(filters.command(["stats", "botstats"]))
async def stats_cmd(_, message: Message):
    stats = await get_global_stats()

    await message.reply_text(
        get_text(
            "stats_caption",
            users=stats["users"],
            groups=stats["groups"],
            games_played=stats["games_played"],
            games_won=stats["games_won"],
            games_lost=stats["games_lost"],
            coins=stats["coins"],
            xp=stats["xp"],
        ),
        reply_markup=back_home_buttons(),
        disable_web_page_preview=True,
    )