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
from yumeko.database.users import get_leaderboard
from yumeko.helpers.buttons import back_home_buttons
from yumeko.locales import get_text


@app.on_message(filters.command(["leaderboard", "top"]))
async def leaderboard_cmd(_, message: Message):
    players = await get_leaderboard(10)

    if not players:
        leaderboard = get_text("leaderboard_empty")
    else:
        lines = []

        medals = ["🥇", "🥈", "🥉"]

        for index, player in enumerate(players, start=1):
            medal = medals[index - 1] if index <= 3 else f"{index}."
            name = player.get("first_name") or "Unknown"
            xp = player.get("xp", 0)
            coins = player.get("coins", 0)

            lines.append(
                f"{medal} <b>{name}</b> — <code>{xp} XP</code> | 💰 <code>{coins}</code>"
            )

        leaderboard = "\n".join(lines)

    await message.reply_text(
        get_text("leaderboard_caption", leaderboard=leaderboard),
        reply_markup=back_home_buttons(),
        disable_web_page_preview=True,
    )