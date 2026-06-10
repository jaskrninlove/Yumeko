# ==========================================================
#  Yumeko Games Bot — Connect Four
#  Copyright (c) 2026 Jass
# ==========================================================

active_connect4_games = {}

ROWS = 6
COLS = 7
MIN_PLAYERS = 2
MAX_PLAYERS = 2

WIN_COINS = 80
WIN_XP = 40
LOSE_XP = 15

EMPTY = "⚪"
P1 = "🔴"
P2 = "🟡"


def create_game(chat_id: int, host):
    game = {
        "chat_id": chat_id,
        "status": "joining",
        "host_id": host.id,
        "players": {
            host.id: {
                "id": host.id,
                "name": host.first_name or "Player",
                "piece": P1,
            }
        },
        "order": [host.id],
        "turn": host.id,
        "board": [[EMPTY for _ in range(COLS)] for _ in range(ROWS)],
        "winner": None,
        "moves": 0,
    }

    active_connect4_games[chat_id] = game
    return game


def get_game(chat_id: int):
    return active_connect4_games.get(chat_id)


def end_game(chat_id: int):
    active_connect4_games.pop(chat_id, None)


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
        "piece": P2,
    }

    game["order"].append(user.id)
    return True, "joined"


def start_game(chat_id: int):
    game = get_game(chat_id)

    if not game:
        return False, "no_game"

    if len(game["players"]) < 2:
        return False, "not_enough"

    game["status"] = "playing"
    game["turn"] = game["order"][0]
    return True, "started"


def current_player(game: dict):
    return game["players"].get(game["turn"])


def other_player(game: dict):
    for uid in game["order"]:
        if uid != game["turn"]:
            return game["players"].get(uid)
    return None


def switch_turn(game: dict):
    game["turn"] = game["order"][1] if game["turn"] == game["order"][0] else game["order"][0]


def drop_piece(chat_id: int, user_id: int, col: int):
    game = get_game(chat_id)

    if not game:
        return False, "no_game", None

    if game["status"] != "playing":
        return False, "not_playing", None

    if user_id != game["turn"]:
        return False, "not_turn", None

    if col < 0 or col >= COLS:
        return False, "invalid_col", None

    row_to_place = None

    for row in range(ROWS - 1, -1, -1):
        if game["board"][row][col] == EMPTY:
            row_to_place = row
            break

    if row_to_place is None:
        return False, "column_full", None

    player = game["players"][user_id]
    piece = player["piece"]

    game["board"][row_to_place][col] = piece
    game["moves"] += 1

    won = check_win(game["board"], row_to_place, col, piece)

    result = {
        "row": row_to_place,
        "col": col,
        "piece": piece,
        "player": player,
        "won": won,
        "draw": False,
    }

    if won:
        game["winner"] = user_id
        game["status"] = "finished"
        return True, "winner", result

    if game["moves"] >= ROWS * COLS:
        game["status"] = "finished"
        result["draw"] = True
        return True, "draw", result

    switch_turn(game)
    return True, "moved", result


def check_win(board, row, col, piece):
    directions = [
        (0, 1),    # horizontal
        (1, 0),    # vertical
        (1, 1),    # diagonal down-right
        (1, -1),   # diagonal down-left
    ]

    for dr, dc in directions:
        count = 1
        count += count_dir(board, row, col, dr, dc, piece)
        count += count_dir(board, row, col, -dr, -dc, piece)

        if count >= 4:
            return True

    return False


def count_dir(board, row, col, dr, dc, piece):
    count = 0
    r = row + dr
    c = col + dc

    while 0 <= r < ROWS and 0 <= c < COLS and board[r][c] == piece:
        count += 1
        r += dr
        c += dc

    return count


def format_board(game: dict):
    lines = []

    lines.append("1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣")

    for row in game["board"]:
        lines.append("".join(row))

    return "\n".join(lines)


def player_line(player: dict):
    return (
        f"{player['piece']} "
        f"<a href=\"tg://user?id={player['id']}\"><b>{player['name']}</b></a>"
    )


def players_text(game: dict):
    lines = []

    for uid in game["order"]:
        p = game["players"][uid]
        lines.append(player_line(p))

    return "\n".join(lines)