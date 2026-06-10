# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
#
#  Developer  : Jass
#  Project    : Yumeko Games Bot
#  Version    : 1.0.0
# ==========================================================

import random
from datetime import datetime

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from yumeko.database.users import add_win, add_loss, add_xp


active_rps_games = {}

RPS_TIMEOUT = 30
WINNER_COINS = 30
WINNER_XP = 15
LOSER_XP = 5
DRAW_XP = 3

CHOICES = {
    "rock": "🪨 Rock",
    "paper": "📄 Paper",
    "scissors": "✂️ Scissors",
}


def create_game(chat_id: int, challenger, target):
    game_id = f"{chat_id}_{challenger.id}_{target.id}_{random.randint(1000, 9999)}"

    active_rps_games[game_id] = {
        "game_id": game_id,
        "chat_id": chat_id,
        "challenger_id": challenger.id,
        "challenger_name": challenger.first_name or "Player",
        "target_id": target.id,
        "target_name": target.first_name or "Player",
        "choices": {},
        "status": "waiting",
        "created_at": datetime.utcnow(),
    }

    return game_id


def get_game(game_id: str):
    return active_rps_games.get(game_id)


def end_game(game_id: str):
    active_rps_games.pop(game_id, None)


def set_choice(game_id: str, user_id: int, choice: str):
    game = get_game(game_id)

    if not game:
        return False, "no_game"

    if game["status"] != "choosing":
        return False, "not_choosing"

    if user_id not in [game["challenger_id"], game["target_id"]]:
        return False, "not_player"

    if user_id in game["choices"]:
        return False, "already_chosen"

    game["choices"][user_id] = choice
    return True, "chosen"


def is_ready(game_id: str):
    game = get_game(game_id)

    if not game:
        return False

    return (
        game["challenger_id"] in game["choices"]
        and game["target_id"] in game["choices"]
    )


def decide_winner(game_id: str):
    game = get_game(game_id)

    if not game:
        return None

    c_id = game["challenger_id"]
    t_id = game["target_id"]

    c_choice = game["choices"].get(c_id)
    t_choice = game["choices"].get(t_id)

    if c_choice == t_choice:
        return {
            "result": "draw",
            "winner_id": None,
            "loser_id": None,
            "challenger_choice": c_choice,
            "target_choice": t_choice,
        }

    wins = {
        "rock": "scissors",
        "paper": "rock",
        "scissors": "paper",
    }

    if wins[c_choice] == t_choice:
        return {
            "result": "win",
            "winner_id": c_id,
            "winner_name": game["challenger_name"],
            "loser_id": t_id,
            "loser_name": game["target_name"],
            "challenger_choice": c_choice,
            "target_choice": t_choice,
        }

    return {
        "result": "win",
        "winner_id": t_id,
        "winner_name": game["target_name"],
        "loser_id": c_id,
        "loser_name": game["challenger_name"],
        "challenger_choice": c_choice,
        "target_choice": t_choice,
    }


async def reward_result(result: dict):
    if not result:
        return

    if result["result"] == "draw":
        return

    await add_win(result["winner_id"], coins=WINNER_COINS, xp=WINNER_XP)
    await add_loss(result["loser_id"], xp=LOSER_XP)


async def reward_draw(challenger_id: int, target_id: int):
    await add_xp(challenger_id, DRAW_XP)
    await add_xp(target_id, DRAW_XP)


def challenge_buttons(game_id: str):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✅ Accept", callback_data=f"rps_accept:{game_id}"),
                InlineKeyboardButton("❌ Decline", callback_data=f"rps_decline:{game_id}"),
            ]
        ]
    )


def choice_buttons(game_id: str):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🪨 Rock", callback_data=f"rps_pick:{game_id}:rock"),
                InlineKeyboardButton("📄 Paper", callback_data=f"rps_pick:{game_id}:paper"),
            ],
            [
                InlineKeyboardButton("✂️ Scissors", callback_data=f"rps_pick:{game_id}:scissors"),
            ],
        ]
    )