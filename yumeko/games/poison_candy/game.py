# ==========================================================
#  Yumeko Games Bot — Poison Candy Game
#  Copyright (c) 2026 Jass
# ==========================================================

import random

active_games = {}

MIN_PLAYERS = 2
MAX_PLAYERS = 10
DEFAULT_SIZE = 5

CANDIES = ["🍬", "🍭", "🍫", "🍪", "🍩", "🍦", "🧁"]


def create_game(chat_id: int, host):
    game = {
        "chat_id": chat_id,
        "host_id": host.id,
        "host_name": host.first_name or "Player",
        "status": "joining",
        "size": DEFAULT_SIZE,
        "players": {},
        "order": [],
        "turn_index": 0,
        "board": [],
        "poisons": {},
        "picked": set(),
        "alive": set(),
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
    }

    game["order"].append(user.id)
    game["alive"].add(user.id)
    return True, "joined"


def format_players(game):
    text = ""

    for i, uid in enumerate(game["order"], 1):
        p = game["players"][uid]
        status = "🟢" if p["alive"] else "💀"
        text += f"{i}. {status} <a href='tg://user?id={uid}'><b>{p['name']}</b></a>\n"

    return text.strip()


def make_board(size: int):
    board = []

    for i in range(size * size):
        board.append({
            "id": i,
            "emoji": random.choice(CANDIES),
            "picked": False,
            "dead": False,
        })

    return board


def start_poison_phase(chat_id: int, size: int = DEFAULT_SIZE):
    game = get_game(chat_id)

    if not game:
        return False

    game["status"] = "poison"
    game["size"] = size
    game["board"] = make_board(size)
    game["poisons"] = {}
    game["picked"] = set()
    game["alive"] = set(game["order"])
    game["turn_index"] = 0

    for uid in game["players"]:
        game["players"][uid]["alive"] = True

    return True


def set_poison(chat_id: int, user_id: int, cell_id: int):
    game = get_game(chat_id)

    if not game:
        return False, "no_game"

    if game["status"] != "poison":
        return False, "not_poison_phase"

    if user_id not in game["players"]:
        return False, "not_player"

    if user_id in game["poisons"]:
        return False, "already_set"

    if cell_id < 0 or cell_id >= len(game["board"]):
        return False, "invalid"

    game["poisons"][user_id] = cell_id
    return True, "set"


def all_poisons_set(game):
    return len(game["poisons"]) == len(game["players"])


def begin_battle(chat_id: int):
    game = get_game(chat_id)

    if not game:
        return False

    game["status"] = "playing"
    game["turn_index"] = 0
    normalize_turn(game)
    return True


def alive_players(game):
    return [uid for uid in game["order"] if uid in game["alive"]]


def current_player(game):
    alive = alive_players(game)

    if not alive:
        return None

    if game["turn_index"] >= len(alive):
        game["turn_index"] = 0

    return alive[game["turn_index"]]


def normalize_turn(game):
    alive = alive_players(game)

    if not alive:
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


def pick_candy(chat_id: int, user_id: int, cell_id: int):
    game = get_game(chat_id)

    if not game:
        return False, "no_game", None

    if game["status"] != "playing":
        return False, "not_playing", None

    if user_id not in game["alive"]:
        return False, "dead", None

    if current_player(game) != user_id:
        return False, "not_turn", None

    if cell_id < 0 or cell_id >= len(game["board"]):
        return False, "invalid", None

    cell = game["board"][cell_id]

    if cell["picked"]:
        return False, "picked", None

    cell["picked"] = True
    game["picked"].add(cell_id)

    poison_owner = None

    for uid, poison_cell in game["poisons"].items():
        if poison_cell == cell_id:
            poison_owner = uid
            break

    result = {
        "cell": cell,
        "cell_id": cell_id,
        "poison": False,
        "poison_owner": poison_owner,
        "winner": None,
    }

    if poison_owner is not None:
        result["poison"] = True
        cell["dead"] = True

        game["alive"].discard(user_id)
        game["players"][user_id]["alive"] = False

        alive = alive_players(game)

        if len(alive) == 1:
            result["winner"] = alive[0]
            game["status"] = "finished"
        else:
            normalize_turn(game)
    else:
        next_turn(game)

    return True, "picked", result


def board_text(game, reveal=False):
    size = game["size"]
    rows = []

    poison_cells = set(game["poisons"].values())

    for r in range(size):
        line = ""

        for c in range(size):
            idx = r * size + c
            cell = game["board"][idx]

            if cell["dead"]:
                line += "💀"
            elif cell["picked"]:
                line += "⬜"
            elif reveal and idx in poison_cells:
                line += "☠️"
            else:
                line += cell["emoji"]

        rows.append(line)

    return "\n".join(rows)


def winner_data(game, user_id):
    return game["players"].get(user_id)