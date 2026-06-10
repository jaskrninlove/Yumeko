# ==========================================================
#  Yumeko Games Bot — Chain Reaction Engine
#  Copyright (c) 2026 Jass
# ==========================================================

from collections import deque
from datetime import datetime

active_games = {}

MIN_PLAYERS = 2
MAX_PLAYERS = 6

ROWS = 6
COLS = 6

WIN_COINS = 120
WIN_XP = 55
LOSE_XP = 12

PLAYER_ORBS = [
    "🔴",
    "🔵",
    "🟢",
    "🟡",
    "🟣",
    "🟠",
]

EMPTY = "⬛"


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
        "moves": 0,
        "board": make_board(),
        "created_at": now_utc(),
    }

    active_games[chat_id] = game
    join_game(chat_id, host)
    return game


def get_game(chat_id: int):
    return active_games.get(chat_id)


def end_game(chat_id: int):
    active_games.pop(chat_id, None)


def make_board():
    return [
        [
            {
                "owner": None,
                "count": 0,
            }
            for _ in range(COLS)
        ]
        for _ in range(ROWS)
    ]


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

    index = len(game["players"])

    game["players"][user.id] = {
        "id": user.id,
        "name": user.first_name or "Player",
        "orb": PLAYER_ORBS[index],
        "alive": True,
        "moves": 0,
        "explosions": 0,
        "cells": 0,
        "orbs": 0,
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
            f"{index}. {status} {player['orb']} "
            f"<a href='tg://user?id={uid}'><b>{player['name']}</b></a>"
        )

    return "\n".join(lines)


def start_game(chat_id: int):
    game = get_game(chat_id)

    if not game:
        return False, "no_game"

    if len(game["players"]) < MIN_PLAYERS:
        return False, "not_enough"

    game["status"] = "playing"
    game["board"] = make_board()
    game["turn_index"] = 0
    game["round"] = 1
    game["moves"] = 0

    for uid, player in game["players"].items():
        player["alive"] = True
        player["moves"] = 0
        player["explosions"] = 0
        player["cells"] = 0
        player["orbs"] = 0

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


def critical_mass(row: int, col: int):
    corners = [
        (0, 0),
        (0, COLS - 1),
        (ROWS - 1, 0),
        (ROWS - 1, COLS - 1),
    ]

    if (row, col) in corners:
        return 2

    if row == 0 or row == ROWS - 1 or col == 0 or col == COLS - 1:
        return 3

    return 4


def neighbors(row: int, col: int):
    possible = [
        (row - 1, col),
        (row + 1, col),
        (row, col - 1),
        (row, col + 1),
    ]

    return [
        (r, c)
        for r, c in possible
        if 0 <= r < ROWS and 0 <= c < COLS
    ]


def refresh_stats(game):
    for player in game["players"].values():
        player["cells"] = 0
        player["orbs"] = 0

    for r in range(ROWS):
        for c in range(COLS):
            cell = game["board"][r][c]
            owner = cell["owner"]

            if owner in game["players"]:
                game["players"][owner]["cells"] += 1
                game["players"][owner]["orbs"] += cell["count"]


def eliminate_empty_players(game):
    # Players cannot be eliminated until every player has played at least one move.
    if game["moves"] < len(game["order"]):
        return []

    eliminated = []

    for uid in list(game["alive"]):
        player = game["players"][uid]

        if player["orbs"] <= 0:
            game["alive"].discard(uid)
            player["alive"] = False
            eliminated.append(uid)

    normalize_turn(game)
    return eliminated


def is_game_over(game):
    return game["status"] == "playing" and len(alive_players(game)) <= 1 and game["moves"] >= len(game["order"])


def get_winner(game):
    alive = alive_players(game)

    if len(alive) == 1:
        return alive[0]

    if not alive:
        return None

    return max(
        alive,
        key=lambda uid: (
            game["players"][uid]["orbs"],
            game["players"][uid]["cells"],
            -game["players"][uid]["moves"],
        ),
    )


def cell_display(game, row: int, col: int):
    cell = game["board"][row][col]

    if not cell["owner"] or cell["count"] == 0:
        return EMPTY

    player = game["players"].get(cell["owner"])

    if not player:
        return EMPTY

    orb = player["orb"]
    count = cell["count"]

    if count <= 1:
        return orb

    # Use keycap count to show stacked orbs without making huge text.
    nums = {
        2: "²",
        3: "³",
        4: "⁴",
    }

    return orb + nums.get(count, str(count))


def board_text(game):
    rows = []

    for r in range(ROWS):
        line = ""

        for c in range(COLS):
            line += cell_display(game, r, c)

        rows.append(line)

    return "\n".join(rows)


def make_move(chat_id: int, user_id: int, row: int, col: int):
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

    if not (0 <= row < ROWS and 0 <= col < COLS):
        return False, "invalid", None

    cell = game["board"][row][col]

    # A player can only place on empty cell or their own cell.
    if cell["owner"] is not None and cell["owner"] != user_id:
        return False, "enemy_cell", None

    player = game["players"][user_id]

    player["moves"] += 1
    game["moves"] += 1

    explosions = resolve_chain(game, user_id, row, col)
    player["explosions"] += explosions

    refresh_stats(game)
    eliminated = eliminate_empty_players(game)

    result = {
        "player": player,
        "row": row,
        "col": col,
        "explosions": explosions,
        "eliminated": eliminated,
        "winner": None,
        "game_over": False,
    }

    if is_game_over(game):
        result["game_over"] = True
        result["winner"] = get_winner(game)
        game["status"] = "finished"
        return True, "moved", result

    next_turn(game)

    return True, "moved", result


def resolve_chain(game, owner_id: int, row: int, col: int):
    q = deque()
    explosions = 0

    cell = game["board"][row][col]
    cell["owner"] = owner_id
    cell["count"] += 1

    if cell["count"] >= critical_mass(row, col):
        q.append((row, col))

    while q:
        r, c = q.popleft()
        cell = game["board"][r][c]

        if cell["count"] < critical_mass(r, c):
            continue

        explosions += 1
        cell["owner"] = None
        cell["count"] = 0

        for nr, nc in neighbors(r, c):
            ncell = game["board"][nr][nc]
            ncell["owner"] = owner_id
            ncell["count"] += 1

            if ncell["count"] >= critical_mass(nr, nc):
                q.append((nr, nc))

    return explosions


def final_scoreboard(game):
    refresh_stats(game)

    ordered = sorted(
        game["players"].values(),
        key=lambda p: (
            p["alive"],
            p["orbs"],
            p["cells"],
            p["explosions"],
        ),
        reverse=True,
    )

    lines = []

    for index, player in enumerate(ordered, 1):
        status = "🏆" if index == 1 else ("🟢" if player["alive"] else "💀")
        lines.append(
            f"{index}. {status} {player['orb']} <b>{player['name']}</b> — "
            f"⚛ {player['orbs']} orbs · "
            f"🔲 {player['cells']} cells · "
            f"💥 {player['explosions']} blasts"
        )

    return "\n".join(lines)