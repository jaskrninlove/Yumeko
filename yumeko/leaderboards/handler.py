# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
#
#  Developer  : Jass
#  Project    : Yumeko Games Bot
#  Version    : 1.0.0
# ==========================================================

from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message

from yumeko.core.database import users_col, db
from yumeko.leaderboards.strings import (
    leaderboard_menu_text,
    board_text,
    unknown_board_text,
)


LIMIT = 10


def user_name(user: dict):
    return (
        user.get("name")
        or user.get("first_name")
        or user.get("username")
        or f"User {user.get('user_id', 'Unknown')}"
    )


async def top_users(field: str, limit: int = LIMIT):
    cursor = (
        users_col.find({field: {"$gt": 0}})
        .sort(field, -1)
        .limit(limit)
    )

    return await cursor.to_list(length=limit)


async def coins_board():
    users = await top_users("coins")
    rows = [
        f"<b>{user_name(u)}</b> — 💰 <code>{u.get('coins', 0):,}</code>"
        for u in users
    ]

    return board_text("💰 <b>Richest Players</b>", rows)


async def xp_board():
    users = await top_users("xp")
    rows = [
        f"<b>{user_name(u)}</b> — ✨ <code>{u.get('xp', 0):,}</code>"
        for u in users
    ]

    return board_text("✨ <b>XP Leaderboard</b>", rows)


async def wins_board():
    users = await top_users("games_won")
    rows = [
        f"<b>{user_name(u)}</b> — 🏆 <code>{u.get('games_won', 0)}</code> wins"
        for u in users
    ]

    return board_text("🏆 <b>Most Wins</b>", rows)


async def couples_board():
    marriages = db["marriages"]

    cursor = (
        marriages.find({"status": "married", "love_points": {"$gt": 0}})
        .sort("love_points", -1)
        .limit(LIMIT)
    )

    couples = await cursor.to_list(length=LIMIT)

    rows = [
        f"<b>{c['user1']['name']}</b> × <b>{c['user2']['name']}</b> — "
        f"❤️ <code>{c.get('love_points', 0)}</code>"
        for c in couples
    ]

    return board_text("💞 <b>Top Couples</b>", rows)


async def mafia_board():
    stats_col = db["mafia_stats"]

    cursor = (
        stats_col.find({"wins": {"$gt": 0}})
        .sort("wins", -1)
        .limit(LIMIT)
    )

    stats = await cursor.to_list(length=LIMIT)

    rows = []

    for s in stats:
        user = await users_col.find_one({"user_id": s["user_id"]})
        name = user_name(user or {"user_id": s["user_id"]})

        rows.append(
            f"<b>{name}</b> — 🎭 <code>{s.get('wins', 0)}</code> wins · "
            f"⭐ <code>{s.get('mvp', 0)}</code> MVP"
        )

    return board_text("🎭 <b>Mafia Legends</b>", rows)


async def reaction_board():
    users = await top_users("reaction.won")

    rows = [
        f"<b>{user_name(u)}</b> — ⚡ <code>{u.get('reaction.won', 0)}</code>"
        for u in users
    ]

    return board_text("⚡ <b>Reaction Champions</b>", rows)


async def leaderboard_cmd(client, message: Message):
    if len(message.command) < 2:
        await message.reply_text(
            leaderboard_menu_text(),
            parse_mode=ParseMode.HTML,
            reply_to_message_id=message.id,
            disable_web_page_preview=True,
        )
        return

    board = message.command[1].lower()

    aliases = {
        "coin": "coins",
        "money": "coins",
        "rich": "coins",
        "exp": "xp",
        "level": "xp",
        "win": "wins",
        "victory": "wins",
        "couple": "couples",
        "love": "couples",
        "mafia": "mafia",
        "mstats": "mafia",
        "reaction": "reaction",
        "react": "reaction",
    }

    board = aliases.get(board, board)

    if board == "coins":
        text = await coins_board()
    elif board == "xp":
        text = await xp_board()
    elif board == "wins":
        text = await wins_board()
    elif board == "couples":
        text = await couples_board()
    elif board == "mafia":
        text = await mafia_board()
    elif board == "reaction":
        text = await reaction_board()
    else:
        text = unknown_board_text()

    await message.reply_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_to_message_id=message.id,
        disable_web_page_preview=True,
    )


def register_leaderboard_handlers(app):
    app.add_handler(
        MessageHandler(
            leaderboard_cmd,
            filters.command(["leaderboard", "lb"]),
        ),
        group=190,
    )