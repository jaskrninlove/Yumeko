# ==========================================================
#  Yumeko Games Bot — Dots & Boxes Engine
#  Copyright (c) 2026 Jass
# ==========================================================

from datetime import datetime

active_games = {}

GRID_SIZE = 4
BOX_SIZE = GRID_SIZE - 1

MIN_PLAYERS = 2
MAX_PLAYERS = 4

WIN_COINS = 110
WIN_XP = 50
LOSE_XP = 12
DRAW_XP = 18

PLAYER_MARKS = ["🔴", "🔵", "🟢", "🟡"]


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
        "h_lines": [[False for _ in range(BOX_SIZE)] for _ in range(GRID_SIZE)],
        "v_lines": [[False for _ in range(GRID_SIZE)] for _ in range(BOX_SIZE)],
        "boxes": [[None for _ in range(BOX_SIZE)] for _ in range(BOX_SIZE)],
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

    index = len(game["players"])

    game["players"][user.id] = {
        "id": user.id,
        "name": user.first_name or "Player",
        "mark": PLAYER_MARKS[index],
        "boxes": 0,
        "moves": 0,
    }

    game["order"].append(user.id)
    return True, "joined"


def format_players(game):
    lines = []

    for index, uid in enumerate(game["order"], 1):
        p = game["players"][uid]
        lines.append(
            f"{index}. {p['mark']} "
            f"<a href='tg://user?id={uid}'><b>{p['name']}</b></a> — "
            f"Boxes: <b>{p['boxes']}</b>"
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
    game["h_lines"] = [[False for _ in range(BOX_SIZE)] for _ in range(GRID_SIZE)]
    game["v_lines"] = [[False for _ in range(GRID_SIZE)] for _ in range(BOX_SIZE)]
    game["boxes"] = [[None for _ in range(BOX_SIZE)] for _ in range(BOX_SIZE)]

    for p in game["players"].values():
        p["boxes"] = 0
        p["moves"] = 0

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

    game["round"] += 1


def is_valid_line(game, line_type: str, row: int, col: int):
    if line_type == "h":
        return (
            0 <= row < GRID_SIZE
            and 0 <= col < BOX_SIZE
            and not game["h_lines"][row][col]
        )

    if line_type == "v":
        return (
            0 <= row < BOX_SIZE
            and 0 <= col < GRID_SIZE
            and not game["v_lines"][row][col]
        )

    return False


def box_completed(game, br: int, bc: int):
    if not (0 <= br < BOX_SIZE and 0 <= bc < BOX_SIZE):
        return False

    if game["boxes"][br][bc] is not None:
        return False

    top = game["h_lines"][br][bc]
    bottom = game["h_lines"][br + 1][bc]
    left = game["v_lines"][br][bc]
    right = game["v_lines"][br][bc + 1]

    return top and bottom and left and right


def claim_completed_boxes(game, user_id: int, line_type: str, row: int, col: int):
    completed = []

    if line_type == "h":
        possible = [
            (row - 1, col),
            (row, col),
        ]
    else:
        possible = [
            (row, col - 1),
            (row, col),
        ]

    for br, bc in possible:
        if box_completed(game, br, bc):
            game["boxes"][br][bc] = user_id
            game["players"][user_id]["boxes"] += 1
            completed.append((br, bc))

    return completed


def draw_line(chat_id: int, user_id: int, line_type: str, row: int, col: int):
    game = get_game(chat_id)

    if not game:
        return False, "no_game", None

    if game["status"] != "playing":
        return False, "not_playing", None

    if user_id not in game["players"]:
        return False, "not_player", None

    if current_player_id(game) != user_id:
        return False, "not_turn", None

    if not is_valid_line(game, line_type, row, col):
        return False, "invalid_line", None

    if line_type == "h":
        game["h_lines"][row][col] = True
    else:
        game["v_lines"][row][col] = True

    player = game["players"][user_id]
    player["moves"] += 1

    completed = claim_completed_boxes(game, user_id, line_type, row, col)

    result = {
        "player": player,
        "line_type": line_type,
        "row": row,
        "col": col,
        "completed": completed,
        "extra_turn": bool(completed),
        "game_over": False,
        "winner": None,
        "draw": False,
    }

    if is_game_over(game):
        result["game_over"] = True
        result["winner"] = get_winner(game)
        result["draw"] = result["winner"] is None
        game["status"] = "finished"
        return True, "finished", result

    if not completed:
        next_turn(game)

    return True, "drawn", result


def is_game_over(game):
    for row in game["h_lines"]:
        if not all(row):
            return False

    for row in game["v_lines"]:
        if not all(row):
            return False

    return True


def get_winner(game):
    scores = [(uid, p["boxes"]) for uid, p in game["players"].items()]
    scores.sort(key=lambda x: x[1], reverse=True)

    if len(scores) < 2:
        return scores[0][0] if scores else None

    if scores[0][1] == scores[1][1]:
        return None

    return scores[0][0]


def board_text(game):
    rows = []

    for r in range(GRID_SIZE):
        dot_line = ""

        for c in range(GRID_SIZE):
            dot_line += "•"

            if c < BOX_SIZE:
                dot_line += "──" if game["h_lines"][r][c] else "  "

        rows.append(dot_line)

        if r < BOX_SIZE:
            box_line = ""

            for c in range(GRID_SIZE):
                box_line += "│" if game["v_lines"][r][c] else " "

                if c < BOX_SIZE:
                    owner = game["boxes"][r][c]
                    if owner:
                        box_line += game["players"][owner]["mark"]
                    else:
                        box_line += "  "

            rows.append(box_line)

    return "\n".join(rows)


def final_scoreboard(game):
    ordered = sorted(
        game["players"].values(),
        key=lambda p: p["boxes"],
        reverse=True,
    )

    lines = []

    for index, p in enumerate(ordered, 1):
        status = "🏆" if index == 1 else "♟"
        lines.append(
            f"{index}. {status} {p['mark']} <b>{p['name']}</b> — "
            f"Boxes: <b>{p['boxes']}</b> · Moves: <b>{p['moves']}</b>"
        )

    return "\n".join(lines)