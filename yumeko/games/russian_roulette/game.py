# ==========================================================
#  Yumeko Games Bot — Russian Roulette Engine
#  Copyright (c) 2026 Jass
# ==========================================================

import random
from datetime import datetime

active_games = {}

MIN_PLAYERS = 2
MAX_PLAYERS = 12

CHAMBERS = 6

WIN_COINS = 100
WIN_XP = 45
LOSE_XP = 10

SAFE_EMOJIS = ["😮", "😰", "😵‍💫", "🥶", "😶‍🌫️"]
BANG_EMOJIS = ["💥", "☠️", "💀", "🔫"]


def now_utc():
    return datetime.utcnow()


def create_game(chat_id: int, host):
    game = {
        "chat_id": chat_id,
        "host_id": host.id,
        "host_name": host.first_name or "Player",
        "status": "joining",
        "players": {},
        "order": [],
        "alive": set(),
        "turn_index": 0,
        "round": 1,
        "chambers": CHAMBERS,
        "bullet": random.randint(1, CHAMBERS),
        "current_chamber": 1,
        "shots_fired": 0,
        "created_at": now_utc(),
    }

    active_games[chat_id] = game
    join_game(chat_id, host)
    return game


def get_game(chat_id: int):
    return active_games.get(chat_id)


def end_game(chat_id: int):
    active_games.pop(chat_id, None)


def join_game(chat_id: int, user):
    game = get_game(chat_id)

    if not game:
        return False, "no_game"

    if game["status"] != "joining":
        return False, "started"

    if user.id in game["players"]:
        return False, "joined"

    if len(game["players"]) >= MAX_PLAYERS:
        return False, "full"

    game["players"][user.id] = {
        "id": user.id,
        "name": user.first_name or "Player",
        "alive": True,
        "shots": 0,
        "survived": 0,
        "eliminated_round": None,
    }

    game["order"].append(user.id)
    game["alive"].add(user.id)

    return True, "joined"


def format_players(game):
    lines = []

    for index, uid in enumerate(game["order"], 1):
        player = game["players"][uid]
        status = "🟢" if player["alive"] else "💀"

        lines.append(
            f"{index}. {status} "
            f"<a href='tg://user?id={uid}'><b>{player['name']}</b></a>"
            f" — 🔫 {player['shots']} shots"
        )

    return "\n".join(lines)


def start_game(chat_id: int):
    game = get_game(chat_id)

    if not game:
        return False, "no_game"

    if len(game["players"]) < MIN_PLAYERS:
        return False, "not_enough"

    game["status"] = "playing"
    game["turn_index"] = 0
    game["round"] = 1
    game["bullet"] = random.randint(1, game["chambers"])
    game["current_chamber"] = 1
    game["shots_fired"] = 0

    for uid in game["players"]:
        game["players"][uid]["alive"] = True
        game["players"][uid]["shots"] = 0
        game["players"][uid]["survived"] = 0
        game["players"][uid]["eliminated_round"] = None

    game["alive"] = set(game["order"])
    normalize_turn(game)

    return True, "started"


def alive_players(game):
    return [uid for uid in game["order"] if uid in game["alive"]]


def current_player_id(game):
    alive = alive_players(game)

    if not alive:
        return None

    if game["turn_index"] >= len(alive):
        game["turn_index"] = 0

    return alive[game["turn_index"]]


def current_player(game):
    uid = current_player_id(game)

    if uid is None:
        return None

    return game["players"].get(uid)


def normalize_turn(game):
    alive = alive_players(game)

    if not alive:
        game["turn_index"] = 0
        return

    if game["turn_index"] >= len(alive):
        game["turn_index"] = 0


def next_turn(game):
    alive = alive_players(game)

    if len(alive) <= 1:
        return

    game["turn_index"] += 1

    if game["turn_index"] >= len(alive):
        game["turn_index"] = 0

    game["round"] += 1


def reload_revolver(game):
    game["bullet"] = random.randint(1, game["chambers"])
    game["current_chamber"] = 1


def pull_trigger(chat_id: int, user_id: int):
    game = get_game(chat_id)

    if not game:
        return False, "no_game", None

    if game["status"] != "playing":
        return False, "not_playing", None

    if user_id not in game["players"]:
        return False, "not_player", None

    if user_id not in game["alive"]:
        return False, "dead", None

    if current_player_id(game) != user_id:
        return False, "not_turn", None

    player = game["players"][user_id]
    chamber = game["current_chamber"]

    player["shots"] += 1
    game["shots_fired"] += 1

    result = {
        "player": player,
        "chamber": chamber,
        "bullet": game["bullet"],
        "bang": False,
        "safe_emoji": random.choice(SAFE_EMOJIS),
        "bang_emoji": random.choice(BANG_EMOJIS),
        "winner": None,
        "game_over": False,
        "reload": False,
    }

    if chamber == game["bullet"]:
        result["bang"] = True

        game["alive"].discard(user_id)
        player["alive"] = False
        player["eliminated_round"] = game["round"]

        alive = alive_players(game)

        if len(alive) <= 1:
            result["game_over"] = True
            result["winner"] = alive[0] if alive else None
            game["status"] = "finished"
            return True, "bang", result

        normalize_turn(game)
        reload_revolver(game)
        result["reload"] = True
        return True, "bang", result

    player["survived"] += 1

    game["current_chamber"] += 1

    if game["current_chamber"] > game["chambers"]:
        reload_revolver(game)
        result["reload"] = True

    next_turn(game)

    return True, "safe", result


def force_winner(game):
    alive = alive_players(game)

    if not alive:
        return None

    if len(alive) == 1:
        return alive[0]

    # If game is stopped early, most survived shots wins.
    return max(
        alive,
        key=lambda uid: (
            game["players"][uid]["survived"],
            -game["players"][uid]["shots"],
        ),
    )


def final_scoreboard(game):
    ordered = sorted(
        game["players"].values(),
        key=lambda p: (
            p["alive"],
            p["survived"],
            -p["shots"],
        ),
        reverse=True,
    )

    lines = []

    for index, player in enumerate(ordered, 1):
        status = "🏆" if index == 1 else ("🟢" if player["alive"] else "💀")
        lines.append(
            f"{index}. {status} <b>{player['name']}</b> — "
            f"😮 survived <b>{player['survived']}</b> · "
            f"🔫 shots <b>{player['shots']}</b>"
        )

    return "\n".join(lines)