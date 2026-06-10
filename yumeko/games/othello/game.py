# ==========================================================
#  Yumeko Games Bot — Othello / Reversi Engine
#  Copyright (c) 2026 Jass
# ==========================================================

from datetime import datetime

active_games = {}

BOARD_SIZE = 8
MIN_PLAYERS = 2
MAX_PLAYERS = 2

BLACK = "⚫"
WHITE = "⚪"
EMPTY = "·"

WIN_COINS = 120
WIN_XP = 55
LOSE_XP = 14
DRAW_XP = 20

DIRECTIONS = [
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1),           (0, 1),
    (1, -1),  (1, 0),  (1, 1),
]


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
                "piece": BLACK,
                "moves": 0,
                "flips": 0,
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
    board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

    mid = BOARD_SIZE // 2
    board[mid - 1][mid - 1] = WHITE
    board[mid][mid] = WHITE
    board[mid - 1][mid] = BLACK
    board[mid][mid - 1] = BLACK

    return board


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
        "piece": WHITE,
        "moves": 0,
        "flips": 0,
    }

    game["order"].append(user.id)
    return True, "joined"


def format_players(game):
    lines = []

    for index, uid in enumerate(game["order"], 1):
        player = game["players"][uid]

        lines.append(
            f"{index}. {player['piece']} "
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
        player["flips"] = 0

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


def next_turn(game):
    game["turn_index"] += 1

    if game["turn_index"] >= len(game["order"]):
        game["turn_index"] = 0


def piece_for_user(game, user_id: int):
    player = game["players"].get(user_id)

    if not player:
        return None

    return player["piece"]


def opponent_piece(piece: str):
    return WHITE if piece == BLACK else BLACK


def in_bounds(row: int, col: int):
    return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE


def flips_for_move(game, row: int, col: int, piece: str):
    if not in_bounds(row, col):
        return []

    if game["board"][row][col] is not None:
        return []

    enemy = opponent_piece(piece)
    all_flips = []

    for dr, dc in DIRECTIONS:
        path = []
        r = row + dr
        c = col + dc

        while in_bounds(r, c) and game["board"][r][c] == enemy:
            path.append((r, c))
            r += dr
            c += dc

        if path and in_bounds(r, c) and game["board"][r][c] == piece:
            all_flips.extend(path)

    return all_flips


def valid_moves_for_piece(game, piece: str):
    moves = []

    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            flips = flips_for_move(game, r, c, piece)
            if flips:
                moves.append((r, c))

    return moves


def valid_moves_for_user(game, user_id: int):
    piece = piece_for_user(game, user_id)

    if not piece:
        return []

    return valid_moves_for_piece(game, piece)


def has_any_valid_move(game, user_id: int):
    return bool(valid_moves_for_user(game, user_id))


def count_pieces(game):
    counts = {
        BLACK: 0,
        WHITE: 0,
    }

    for row in game["board"]:
        for cell in row:
            if cell in counts:
                counts[cell] += 1

    return counts


def is_board_full(game):
    for row in game["board"]:
        for cell in row:
            if cell is None:
                return False

    return True


def both_no_moves(game):
    for uid in game["order"]:
        if valid_moves_for_user(game, uid):
            return False

    return True


def determine_winner(game):
    counts = count_pieces(game)
    black_count = counts[BLACK]
    white_count = counts[WHITE]

    if black_count == white_count:
        return None

    winning_piece = BLACK if black_count > white_count else WHITE

    for uid, player in game["players"].items():
        if player["piece"] == winning_piece:
            return uid

    return None


def is_game_over(game):
    return is_board_full(game) or both_no_moves(game)


def place_piece(chat_id: int, user_id: int, row: int, col: int):
    game = get_game(chat_id)

    if not game:
        return False, "no_game", None

    if game["status"] != "playing":
        return False, "not_playing", None

    if user_id not in game["players"]:
        return False, "not_player", None

    if current_player_id(game) != user_id:
        return False, "not_turn", None

    piece = piece_for_user(game, user_id)

    if not piece:
        return False, "not_player", None

    flips = flips_for_move(game, row, col, piece)

    if not flips:
        return False, "invalid_move", None

    game["board"][row][col] = piece

    for fr, fc in flips:
        game["board"][fr][fc] = piece

    player = game["players"][user_id]
    player["moves"] += 1
    player["flips"] += len(flips)
    game["moves"] += 1

    result = {
        "player": player,
        "row": row,
        "col": col,
        "flips": len(flips),
        "skipped": None,
        "winner": None,
        "draw": False,
        "game_over": False,
        "counts": count_pieces(game),
    }

    if is_game_over(game):
        result["game_over"] = True
        result["winner"] = determine_winner(game)
        result["draw"] = result["winner"] is None
        game["winner"] = result["winner"]
        game["status"] = "finished"
        return True, "finished", result

    next_turn(game)

    # If next player has no valid move, skip them.
    next_uid = current_player_id(game)

    if next_uid is not None and not has_any_valid_move(game, next_uid):
        skipped_player = game["players"][next_uid]
        result["skipped"] = skipped_player
        next_turn(game)

    if is_game_over(game):
        result["game_over"] = True
        result["winner"] = determine_winner(game)
        result["draw"] = result["winner"] is None
        game["winner"] = result["winner"]
        game["status"] = "finished"

    result["counts"] = count_pieces(game)

    return True, "placed", result


def cell_display(game, row: int, col: int):
    cell = game["board"][row][col]

    if cell is None:
        return EMPTY

    return cell


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
    counts = count_pieces(game)
    lines = []

    for index, uid in enumerate(game["order"], 1):
        player = game["players"][uid]
        piece_count = counts[player["piece"]]
        status = "🏆" if uid == game.get("winner") else "♟"

        lines.append(
            f"{index}. {status} {player['piece']} "
            f"<b>{player['name']}</b> — "
            f"Pieces: <b>{piece_count}</b> · "
            f"Flips: <b>{player['flips']}</b>"
        )

    return "\n".join(lines)