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

import random
from datetime import datetime

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from yumeko.database.users import add_win, add_loss
from yumeko.database.groups import add_group_game


active_typing_games = {}

MIN_PLAYERS = 2
WINNER_COINS = 70
WINNER_XP = 35
LOSER_XP = 7

SENTENCES = [
    "Yumeko loves the thrill of every game",
    "Fast fingers can defeat slow minds",
    "A true gambler never fears the final round",
    "The keyboard becomes your weapon tonight",
    "One mistake and fate will laugh at you",
    "Victory belongs to the fastest soul",
    "Type carefully because Yumeko is watching",
]


def create_game(chat_id: int, host_id: int, host_name: str):
    active_typing_games[chat_id] = {
        "host_id": host_id,
        "host_name": host_name,
        "players": {},
        "status": "joining",
        "sentence": None,
        "winner": None,
        "started_at": datetime.utcnow(),
    }


def get_game(chat_id: int):
    return active_typing_games.get(chat_id)


def end_game(chat_id: int):
    active_typing_games.pop(chat_id, None)


def join_game(chat_id: int, user):
    game = get_game(chat_id)

    if not game:
        return False, "no_game"

    if game["status"] != "joining":
        return False, "already_started"

    if user.id in game["players"]:
        return False, "already_joined"

    game["players"][user.id] = {
        "id": user.id,
        "name": user.first_name or "Unknown",
        "username": user.username,
    }

    return True, "joined"


def start_round(chat_id: int):
    game = get_game(chat_id)

    if not game:
        return None

    sentence = random.choice(SENTENCES)
    game["sentence"] = sentence
    game["status"] = "running"

    return sentence


async def reward_winner(chat_id: int, winner_id: int):
    game = get_game(chat_id)

    if not game:
        return

    for user_id in game["players"]:
        if user_id == winner_id:
            await add_win(user_id, coins=WINNER_COINS, xp=WINNER_XP)
        else:
            await add_loss(user_id, xp=LOSER_XP)

    await add_group_game(chat_id)


def lobby_buttons():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("⌨️ Join Race", callback_data="typing_join"),
                InlineKeyboardButton("🚀 Start", callback_data="typing_start"),
            ],
            [InlineKeyboardButton("❌ Cancel", callback_data="typing_cancel")],
        ]
    )


def format_players(players: dict):
    if not players:
        return "No players joined yet."

    return "\n".join(
        f"{i}. <b>{p['name']}</b>"
        for i, p in enumerate(players.values(), start=1)
    )