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
from yumeko.database.groups import add_group_game


active_bomb_games = {}

MIN_PLAYERS = 2
MAX_PLAYERS = 50
JOIN_TIME = 30
TURN_TIME = 15
PLAYER_LIVES = 3

VALID_WORD_XP = 2
LOSER_XP = 10
WINNER_COINS = 150
WINNER_XP = 75

EASY_SYLLABLES = ["a", "e", "i", "o", "u", "ca", "ma", "ra", "ta", "la", "pa", "go"]
MEDIUM_SYLLABLES = ["ing", "ion", "ent", "ter", "str", "cha", "tra", "ble", "com"]
HARD_SYLLABLES = ["tion", "ment", "able", "ough", "ness", "ship", "less", "ance"]


def create_game(chat_id: int, host_id: int, host_name: str):
    active_bomb_games[chat_id] = {
        "host_id": host_id,
        "host_name": host_name,
        "players": {},
        "alive": [],
        "used_words": [],
        "current_player_index": 0,
        "current_syllable": None,
        "turn_token": 0,
        "round": 1,
        "status": "joining",
        "started_at": datetime.utcnow(),
    }


def get_game(chat_id: int):
    return active_bomb_games.get(chat_id)


def end_game(chat_id: int):
    active_bomb_games.pop(chat_id, None)


def join_game(chat_id: int, user):
    game = get_game(chat_id)

    if not game:
        return False, "no_game"

    if game["status"] != "joining":
        return False, "already_started"

    if user.id in game["players"]:
        return False, "already_joined"

    if len(game["players"]) >= MAX_PLAYERS:
        return False, "full"

    game["players"][user.id] = {
        "id": user.id,
        "name": user.first_name or "Unknown",
        "username": user.username,
        "score": 0,
        "words": 0,
        "lives": PLAYER_LIVES,
    }

    game["alive"].append(user.id)
    return True, "joined"


def join_button():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("💣 Join Bomb Party", callback_data="bomb_join")]]
    )


def pick_syllable(game: dict):
    if game["round"] >= 12:
        return random.choice(HARD_SYLLABLES)
    if game["round"] >= 6:
        return random.choice(MEDIUM_SYLLABLES)
    return random.choice(EASY_SYLLABLES)


def start_game(chat_id: int):
    game = get_game(chat_id)

    if not game:
        return None

    random.shuffle(game["alive"])
    game["status"] = "running"
    game["current_player_index"] = 0
    game["round"] = 1
    game["current_syllable"] = pick_syllable(game)
    game["turn_token"] += 1

    return get_current_player(chat_id)


def get_current_player(chat_id: int):
    game = get_game(chat_id)

    if not game or not game["alive"]:
        return None

    if game["current_player_index"] >= len(game["alive"]):
        game["current_player_index"] = 0

    user_id = game["alive"][game["current_player_index"]]
    return game["players"].get(user_id)


def move_next(game: dict):
    game["current_player_index"] += 1

    if game["current_player_index"] >= len(game["alive"]):
        game["current_player_index"] = 0
        game["round"] += 1

    game["current_syllable"] = pick_syllable(game)
    game["turn_token"] += 1


def validate_word(chat_id: int, user_id: int, text: str):
    game = get_game(chat_id)

    if not game:
        return False, "no_game"

    if game["status"] != "running":
        return False, "not_running"

    player = get_current_player(chat_id)

    if not player or player["id"] != user_id:
        return False, "not_turn"

    word = text.strip().lower()

    if not word.isalpha():
        return False, "invalid"

    if len(word) < 3:
        return False, "too_short"

    if word in game["used_words"]:
        return False, "used"

    if game["current_syllable"] not in word:
        return False, "missing"

    game["used_words"].append(word)
    player["words"] += 1
    player["score"] += len(word)

    move_next(game)

    return True, word


def timeout_current_player(chat_id: int, token: int):
    game = get_game(chat_id)

    if not game:
        return None, "no_game"

    if game["status"] != "running":
        return None, "not_running"

    if token != game["turn_token"]:
        return None, "old_turn"

    player = get_current_player(chat_id)

    if not player:
        return None, "no_player"

    player["lives"] -= 1

    eliminated = False

    if player["lives"] <= 0:
        eliminated = True
        uid = player["id"]

        if uid in game["alive"]:
            game["alive"].remove(uid)

        if game["current_player_index"] >= len(game["alive"]):
            game["current_player_index"] = 0
    else:
        move_next(game)
        return player, "life_lost"

    game["current_syllable"] = pick_syllable(game)
    game["turn_token"] += 1

    return player, "eliminated" if eliminated else "life_lost"


def has_winner(chat_id: int):
    game = get_game(chat_id)

    if not game:
        return None

    if len(game["alive"]) == 1:
        return game["players"].get(game["alive"][0])

    return None


async def reward_valid_word(user_id: int):
    await add_xp(user_id, VALID_WORD_XP)


async def reward_final(chat_id: int, winner_id: int):
    game = get_game(chat_id)

    if not game:
        return

    for user_id in game["players"]:
        if user_id == winner_id:
            await add_win(user_id, coins=WINNER_COINS, xp=WINNER_XP)
        else:
            await add_loss(user_id, xp=LOSER_XP)

    await add_group_game(chat_id)


def format_players(game: dict):
    if not game or not game["players"]:
        return "No players joined yet."

    return "\n".join(
        f"{i}. <b>{p['name']}</b>"
        for i, p in enumerate(game["players"].values(), start=1)
    )


def format_alive(game: dict):
    if not game or not game["alive"]:
        return "No survivors."

    lines = []
    for i, uid in enumerate(game["alive"], start=1):
        p = game["players"].get(uid, {})
        lines.append(
            f"{i}. <b>{p.get('name', 'Unknown')}</b> — ❤️ <code>{p.get('lives', 0)}</code>"
        )
    return "\n".join(lines)


def format_scores(game: dict):
    if not game or not game["players"]:
        return "No scores."

    rows = sorted(
        game["players"].values(),
        key=lambda p: p.get("score", 0),
        reverse=True,
    )

    return "\n".join(
        f"{i}. <b>{p['name']}</b> — <code>{p['score']}</code> pts | <code>{p['words']}</code> words"
        for i, p in enumerate(rows, start=1)
    )