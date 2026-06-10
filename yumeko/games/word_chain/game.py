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

from yumeko.database.users import add_win, add_loss, add_xp, add_coins
from yumeko.database.groups import add_group_game


active_wordchain_games = {}

MIN_PLAYERS = 2
MAX_PLAYERS = 50
JOIN_TIME = 60

BASE_TURN_TIME = 30
MIN_TURN_TIME = 15

WORDS_PER_TURN = 1
PLAYER_LIVES = 3

LOSER_XP = 8
WINNER_COINS = 120
WINNER_XP = 60

START_LETTERS = list("abcdefghijklmnopqrstuvwxyz")


def create_game(chat_id: int, host_id: int, host_name: str):
    active_wordchain_games[chat_id] = {
        "host_id": host_id,
        "host_name": host_name,
        "players": {},
        "alive": [],
        "used_words": [],
        "current_player_index": 0,
        "current_word_count": 0,
        "current_letter": random.choice(START_LETTERS),
        "required_length": 3,
        "turn_token": 0,
        "status": "joining",
        "started_at": datetime.utcnow(),
    }


def get_game(chat_id: int):
    return active_wordchain_games.get(chat_id)


def end_game(chat_id: int):
    active_wordchain_games.pop(chat_id, None)


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


def start_game(chat_id: int):
    game = get_game(chat_id)

    if not game:
        return None

    random.shuffle(game["alive"])
    game["status"] = "running"
    game["current_player_index"] = 0
    game["current_word_count"] = 0
    game["turn_token"] += 1

    return get_current_player(chat_id)


def join_button():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔤 Join Word Chain", callback_data="wc_join")]]
    )


def get_current_player(chat_id: int):
    game = get_game(chat_id)

    if not game or not game["alive"]:
        return None

    if game["current_player_index"] >= len(game["alive"]):
        game["current_player_index"] = 0

    user_id = game["alive"][game["current_player_index"]]
    return game["players"].get(user_id)


def increase_difficulty(game: dict):
    total = len(game["used_words"])

    if total >= 85:
        game["required_length"] = 12
    elif total >= 65:
        game["required_length"] = 11
    elif total >= 45:
        game["required_length"] = 10
    elif total >= 25:
        game["required_length"] = 8
    elif total >= 12:
        game["required_length"] = 5
    else:
        game["required_length"] = 3


def get_turn_time(game: dict):
    length = game.get("required_length", 3)

    if length <= 3:
        return 30
    if length <= 5:
        return 26
    if length <= 8:
        return 22
    if length <= 10:
        return 18

    return MIN_TURN_TIME


def get_word_reward(word: str):
    length = len(word)

    if length >= 12:
        return 10, 12
    if length >= 10:
        return 8, 10
    if length >= 8:
        return 6, 7
    if length >= 5:
        return 4, 4

    return 2, 2


def move_to_next_player(game: dict):
    game["current_word_count"] = 0
    game["current_player_index"] += 1

    if game["current_player_index"] >= len(game["alive"]):
        game["current_player_index"] = 0


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

    if len(word) < game["required_length"]:
        return False, "too_short"

    if word in game["used_words"]:
        return False, "used"

    if not word.startswith(game["current_letter"]):
        return False, "wrong_letter"

    xp_reward, coin_reward = get_word_reward(word)

    game["used_words"].append(word)
    player["score"] += len(word) + xp_reward
    player["words"] += 1

    game["current_word_count"] += 1
    game["current_letter"] = word[-1]

    increase_difficulty(game)

    if game["current_word_count"] >= WORDS_PER_TURN:
        move_to_next_player(game)

    game["turn_token"] += 1

    return True, {
        "word": word,
        "xp": xp_reward,
        "coins": coin_reward,
        "length": len(word),
    }


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
        user_id = player["id"]

        if user_id in game["alive"]:
            game["alive"].remove(user_id)

        if game["current_player_index"] >= len(game["alive"]):
            game["current_player_index"] = 0
    else:
        move_to_next_player(game)

    game["turn_token"] += 1

    return player, "eliminated" if eliminated else "life_lost"


def has_winner(chat_id: int):
    game = get_game(chat_id)

    if not game:
        return None

    if len(game["alive"]) == 1:
        return game["players"].get(game["alive"][0])

    return None


async def reward_valid_word(user_id: int, reward: dict):
    await add_xp(user_id, reward.get("xp", 2))
    await add_coins(user_id, reward.get("coins", 2))


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
            f'{i}. <a href="tg://user?id={uid}">{p.get("name", "Unknown")}</a> — ❤️ <code>{p.get("lives", 0)}</code>'
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
        f'{i}. <a href="tg://user?id={p["id"]}">{p["name"]}</a> — <code>{p["score"]}</code> pts | <code>{p["words"]}</code> words'
        for i, p in enumerate(rows, start=1)
    )