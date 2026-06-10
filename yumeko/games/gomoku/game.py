# ==========================================================
#  Yumeko Games Bot — Gomoku Engine
#  Copyright (c) 2026 Jass
# ==========================================================

from datetime import datetime

active_games = {}

BOARD_SIZE = 9
WIN_LENGTH = 5

MIN_PLAYERS = 2
MAX_PLAYERS = 2

BLACK = "⚫"
WHITE = "⚪"
EMPTY = "·"

WIN_COINS = 110
WIN_XP = 50
LOSE_XP = 12


def now_utc():
    return datetime.utcnow()


def create_game(chat_id: int, host):
    game = {
        "chat_id": chat_id,
        "host_id": host.id,
        "host_name": host.first_name or "Player",
        "status": "joining",
        "players": {
            host.id: {
                "id": host.id,
                "name": host.first_name or "Player",
                "stone": BLACK,
                "moves": 0,
            }
        },
        "order": [host.id],
        "turn_index": 0,
        "board": make_board(),
        "moves": 0,
        "winner": None,
        "created_at": now_utc(),
    }

    active_games[chat_id] = game
    return game


def get_game(chat_id: int):
    return active_games.get(chat_id)


def end_game(chat_id: int):
    active_games.pop(chat_id, None)


def make_board():
    return [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]


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
        "stone": WHITE,
        "moves": 0,
    }

    game["order"].append(user.id)
    return True, "joined"


def format_players(game):
    lines = []

    for index, uid in enumerate(game["order"], 1):
        player = game["players"][uid]
        lines.append(
            f"{index}. {player['stone']} "
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
    game["moves"] = 0
    game["winner"] = None

    for player in game["players"].values():
        player["moves"] = 0

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


def next_turn(game):
    game["turn_index"] += 1

    if game["turn_index"] >= len(game["order"]):
        game["turn_index"] = 0


def place_stone(chat_id: int, user_id: int, row: int, col: int):
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

    if game["board"][row][col] is not None:
        return False, "occupied", None

    player = game["players"][user_id]
    stone = player["stone"]

    game["board"][row][col] = user_id
    game["moves"] += 1
    player["moves"] += 1

    won = check_win(game, row, col, user_id)

    result = {
        "player": player,
        "row": row,
        "col": col,
        "won": won,
        "draw": False,
        "winner": None,
    }

    if won:
        game["winner"] = user_id
        game["status"] = "finished"
        result["winner"] = user_id
        return True, "win", result

    if game["moves"] >= BOARD_SIZE * BOARD_SIZE:
        game["status"] = "finished"
        result["draw"] = True
        return True, "draw", result

    next_turn(game)
    return True, "placed", result


def check_win(game, row: int, col: int, user_id: int):
    directions = [
        (0, 1),    # horizontal
        (1, 0),    # vertical
        (1, 1),    # diagonal down-right
        (1, -1),   # diagonal down-left
    ]

    for dr, dc in directions:
        count = 1
        count += count_direction(game, row, col, dr, dc, user_id)
        count += count_direction(game, row, col, -dr, -dc, user_id)

        if count >= WIN_LENGTH:
            return True

    return False


def count_direction(game, row: int, col: int, dr: int, dc: int, user_id: int):
    count = 0
    r = row + dr
    c = col + dc

    while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
        if game["board"][r][c] != user_id:
            break

        count += 1
        r += dr
        c += dc

    return count


def cell_display(game, row: int, col: int):
    owner = game["board"][row][col]

    if owner is None:
        return EMPTY

    player = game["players"].get(owner)

    if not player:
        return EMPTY

    return player["stone"]


def board_text(game):
    rows = []

    header = "  " + "".join(str(i + 1) for i in range(BOARD_SIZE))
    rows.append(header)

    for r in range(BOARD_SIZE):
        line = f"{r + 1} "
        for c in range(BOARD_SIZE):
            line += cell_display(game, r, c)
        rows.append(line)

    return "\n".join(rows)


def final_scoreboard(game):
    lines = []

    for index, uid in enumerate(game["order"], 1):
        player = game["players"][uid]
        status = "🏆" if uid == game.get("winner") else "♟"
        lines.append(
            f"{index}. {status} {player['stone']} "
            f"<b>{player['name']}</b> — "
            f"Moves: <b>{player['moves']}</b>"
        )

    return "\n".join(lines)