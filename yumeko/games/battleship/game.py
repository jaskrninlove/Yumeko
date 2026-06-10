# ==========================================================
#  Yumeko Games Bot — Battleship Royale Engine
#  Copyright (c) 2026 Jass
# ==========================================================

import random
from datetime import datetime

active_games = {}

BOARD_SIZE = 6
MIN_PLAYERS = 2
MAX_PLAYERS = 2

WATER = "🌊"
SHIP = "🚢"
HIT = "💥"
MISS = "⭕"
SUNK = "💀"
UNKNOWN = "⬛"

WIN_COINS = 140
WIN_XP = 65
LOSE_XP = 15

SHIPS = [
    {"name": "Battleship", "size": 3},
    {"name": "Destroyer", "size": 2},
    {"name": "Patrol", "size": 2},
]


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
        "turn_index": 0,
        "round": 1,
        "winner": None,
        "created_at": now_utc(),
    }

    active_games[chat_id] = game
    join_game(chat_id, host)
    return game


def get_game(chat_id: int):
    return active_games.get(chat_id)


def end_game(chat_id: int):
    active_games.pop(chat_id, None)


def empty_board():
    return [
        [
            {
                "ship": None,
                "hit": False,
                "miss": False,
            }
            for _ in range(BOARD_SIZE)
        ]
        for _ in range(BOARD_SIZE)
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

    game["players"][user.id] = {
        "id": user.id,
        "name": user.first_name or "Player",
        "board": empty_board(),
        "ships": [],
        "shots": 0,
        "hits": 0,
        "misses": 0,
        "sunk": 0,
    }

    game["order"].append(user.id)
    return True, "joined"


def format_players(game):
    lines = []

    for index, uid in enumerate(game["order"], 1):
        player = game["players"][uid]
        icon = "🚢" if index == 1 else "⚓"

        lines.append(
            f"{index}. {icon} "
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
    game["turn_index"] = 0
    game["round"] = 1
    game["winner"] = None

    for player in game["players"].values():
        player["board"] = empty_board()
        player["ships"] = []
        player["shots"] = 0
        player["hits"] = 0
        player["misses"] = 0
        player["sunk"] = 0
        auto_place_ships(player)

    return True, "started"


def current_player_id(game):
    if not game["order"]:
        return None

    if game["turn_index"] >= len(game["order"]):
        game["turn_index"] = 0

    return game["order"][game["turn_index"]]


def current_player(game):
    uid = current_player_id(game)

    if uid is None:
        return None

    return game["players"].get(uid)


def opponent_id(game, user_id: int):
    for uid in game["order"]:
        if uid != user_id:
            return uid
    return None


def opponent_player(game, user_id: int):
    oid = opponent_id(game, user_id)

    if oid is None:
        return None

    return game["players"].get(oid)


def next_turn(game):
    game["turn_index"] += 1

    if game["turn_index"] >= len(game["order"]):
        game["turn_index"] = 0

    game["round"] += 1


def can_place(board, row, col, size, horizontal):
    if horizontal:
        if col + size > BOARD_SIZE:
            return False

        cells = [(row, col + i) for i in range(size)]
    else:
        if row + size > BOARD_SIZE:
            return False

        cells = [(row + i, col) for i in range(size)]

    for r, c in cells:
        if board[r][c]["ship"] is not None:
            return False

    return True


def place_ship(board, ship_id, row, col, size, horizontal):
    cells = []

    for i in range(size):
        r = row
        c = col

        if horizontal:
            c += i
        else:
            r += i

        board[r][c]["ship"] = ship_id
        cells.append((r, c))

    return cells


def auto_place_ships(player):
    board = player["board"]
    ships = []

    for index, ship in enumerate(SHIPS):
        placed = False

        for _ in range(200):
            horizontal = random.choice([True, False])
            row = random.randint(0, BOARD_SIZE - 1)
            col = random.randint(0, BOARD_SIZE - 1)

            if can_place(board, row, col, ship["size"], horizontal):
                ship_id = f"s{index}"
                cells = place_ship(
                    board,
                    ship_id,
                    row,
                    col,
                    ship["size"],
                    horizontal,
                )

                ships.append(
                    {
                        "id": ship_id,
                        "name": ship["name"],
                        "size": ship["size"],
                        "cells": cells,
                        "hits": set(),
                        "sunk": False,
                    }
                )

                placed = True
                break

        if not placed:
            # Very rare fallback: reset and retry everything.
            player["board"] = empty_board()
            player["ships"] = []
            return auto_place_ships(player)

    player["ships"] = ships


def get_ship(player, ship_id):
    for ship in player["ships"]:
        if ship["id"] == ship_id:
            return ship
    return None


def all_ships_sunk(player):
    return all(ship["sunk"] for ship in player["ships"])


def attack(chat_id: int, user_id: int, row: int, col: int):
    game = get_game(chat_id)

    if not game:
        return False, "no_game", None

    if game["status"] != "playing":
        return False, "not_playing", None

    if user_id not in game["players"]:
        return False, "not_player", None

    if current_player_id(game) != user_id:
        return False, "not_turn", None

    if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
        return False, "invalid", None

    attacker = game["players"][user_id]
    defender_id = opponent_id(game, user_id)
    defender = game["players"][defender_id]

    cell = defender["board"][row][col]

    if cell["hit"] or cell["miss"]:
        return False, "already", None

    attacker["shots"] += 1

    result = {
        "attacker": attacker,
        "defender": defender,
        "row": row,
        "col": col,
        "hit": False,
        "miss": False,
        "sunk": None,
        "winner": None,
        "game_over": False,
    }

    if cell["ship"] is None:
        cell["miss"] = True
        attacker["misses"] += 1
        result["miss"] = True
        next_turn(game)
        return True, "miss", result

    cell["hit"] = True
    attacker["hits"] += 1
    result["hit"] = True

    ship = get_ship(defender, cell["ship"])

    if ship:
        ship["hits"].add((row, col))

        if len(ship["hits"]) >= ship["size"]:
            ship["sunk"] = True
            attacker["sunk"] += 1
            result["sunk"] = ship

    if all_ships_sunk(defender):
        game["status"] = "finished"
        game["winner"] = user_id
        result["winner"] = user_id
        result["game_over"] = True
        return True, "win", result

    # Hit gives extra turn for more fun.
    return True, "hit", result


def own_board_text(player):
    rows = ["  1 2 3 4 5 6"]

    for r in range(BOARD_SIZE):
        line = f"{chr(65 + r)} "

        for c in range(BOARD_SIZE):
            cell = player["board"][r][c]

            if cell["hit"]:
                line += HIT
            elif cell["miss"]:
                line += MISS
            elif cell["ship"]:
                line += SHIP
            else:
                line += WATER

        rows.append(line)

    return "\n".join(rows)


def enemy_board_text(enemy):
    rows = ["  1 2 3 4 5 6"]

    for r in range(BOARD_SIZE):
        line = f"{chr(65 + r)} "

        for c in range(BOARD_SIZE):
            cell = enemy["board"][r][c]

            if cell["hit"]:
                line += HIT
            elif cell["miss"]:
                line += MISS
            else:
                line += UNKNOWN

        rows.append(line)

    return "\n".join(rows)


def final_scoreboard(game):
    lines = []

    for index, uid in enumerate(game["order"], 1):
        player = game["players"][uid]
        status = "🏆" if uid == game.get("winner") else "⚓"

        lines.append(
            f"{index}. {status} <b>{player['name']}</b> — "
            f"🎯 Hits: <b>{player['hits']}</b> · "
            f"⭕ Misses: <b>{player['misses']}</b> · "
            f"💀 Sunk: <b>{player['sunk']}</b>"
        )

    return "\n".join(lines)