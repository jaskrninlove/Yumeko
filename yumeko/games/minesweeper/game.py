# ==========================================================
#  Yumeko Games Bot — Minesweeper Game Logic
#  Copyright (c) 2026 Jass  |  Version 2.0.0
# ==========================================================

import random
from datetime import datetime
from typing import Optional

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from yumeko.games.minesweeper import strings as S

# ── Constants ─────────────────────────────────────────────
REWARD_COINS   = 60
REWARD_XP      = 30
LOSER_XP       = 10
PERFECT_BONUS  = 40
MIN_PLAYERS    = 1
MAX_PLAYERS    = 10
JOIN_TIMEOUT   = 60
MAX_LIVES      = 3

# Board sizes per difficulty
DIFFICULTIES = {
    "easy":   {"rows": 5, "cols": 5, "mines": 4},
    "medium": {"rows": 6, "cols": 6, "mines": 7},
    "hard":   {"rows": 7, "cols": 7, "mines": 12},
}
DEFAULT_DIFF = "medium"

active_games: dict[int, dict] = {}


# ── Board generation ──────────────────────────────────────

def _generate_board(rows: int, cols: int, mine_count: int,
                    safe_start: Optional[tuple] = None) -> list[list[int]]:
    """Returns board where -1 = mine, 0-8 = adjacent mine count."""
    board = [[0] * cols for _ in range(rows)]

    # Place mines avoiding the first tap
    all_cells = [(r, c) for r in range(rows) for c in range(cols)]
    if safe_start:
        # Exclude first tap + its neighbours from mine placement
        sr, sc = safe_start
        avoid = {(sr + dr, sc + dc)
                 for dr in range(-1, 2) for dc in range(-1, 2)
                 if 0 <= sr + dr < rows and 0 <= sc + dc < cols}
        candidates = [cell for cell in all_cells if cell not in avoid]
    else:
        candidates = all_cells

    mine_cells = set(random.sample(candidates, min(mine_count, len(candidates))))

    for r, c in mine_cells:
        board[r][c] = -1

    # Calculate adjacent counts
    for r in range(rows):
        for c in range(cols):
            if board[r][c] == -1:
                continue
            count = 0
            for dr in range(-1, 2):
                for dc in range(-1, 2):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] == -1:
                        count += 1
            board[r][c] = count

    return board


def _count_safe(board: list[list[int]]) -> int:
    return sum(1 for row in board for cell in row if cell != -1)


def _flood_fill(board: list[list[int]],
                revealed: list[list[bool]],
                flagged: list[list[bool]],
                row: int, col: int) -> int:
    """Auto-reveal all connected 0-cells. Returns number of newly revealed cells."""
    rows, cols = len(board), len(board[0])
    stack  = [(row, col)]
    count  = 0
    visited = set()

    while stack:
        r, c = stack.pop()
        if (r, c) in visited:
            continue
        visited.add((r, c))
        if revealed[r][c] or flagged[r][c]:
            continue
        revealed[r][c] = True
        count += 1
        if board[r][c] == 0:
            for dr in range(-1, 2):
                for dc in range(-1, 2):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited:
                        stack.append((nr, nc))

    return count


# ── State ─────────────────────────────────────────────────

def create_game(chat_id: int, host_id: int, host_name: str,
                mode: str = "rival", difficulty: str = DEFAULT_DIFF):
    diff = DIFFICULTIES.get(difficulty, DIFFICULTIES[DEFAULT_DIFF])
    active_games[chat_id] = {
        "host_id":    host_id,
        "host_name":  host_name,
        "mode":       mode,
        "difficulty": difficulty,
        "rows":       diff["rows"],
        "cols":       diff["cols"],
        "mine_count": diff["mines"],
        "players":    {},
        "status":     "joining",
        "started_at": datetime.utcnow(),
    }


def get_game(chat_id: int): return active_games.get(chat_id)
def end_game(chat_id: int): active_games.pop(chat_id, None)


def join_game(chat_id: int, user):
    game = get_game(chat_id)
    if not game:                            return False, "no_game"
    if game["status"] != "joining":         return False, "started"
    if len(game["players"]) >= MAX_PLAYERS: return False, "full"
    if user.id in game["players"]:          return False, "joined"

    rows = game["rows"]
    cols = game["cols"]
    game["players"][user.id] = {
        "name":     user.first_name or "Unknown",
        "lives":    MAX_LIVES,
        "alive":    True,
        "board":    None,               # generated on first tap
        "revealed": [[False] * cols for _ in range(rows)],
        "flagged":  [[False] * cols for _ in range(rows)],
        "safe_count": 0,
        "total_safe": 0,
    }
    return True, "ok"


def init_player_board(chat_id: int, user_id: int, first_row: int, first_col: int):
    """Generate a board after the first tap so it's never a mine."""
    game   = get_game(chat_id)
    player = game["players"][user_id]
    rows, cols = game["rows"], game["cols"]
    board  = _generate_board(rows, cols, game["mine_count"],
                             safe_start=(first_row, first_col))
    player["board"]       = board
    player["total_safe"]  = _count_safe(board)


def reveal_cell(chat_id: int, user_id: int,
                row: int, col: int) -> dict:
    """
    Returns dict with keys:
      result: "mine" | "safe" | "already" | "dead" | "win"
      newly_revealed: int
      lives_left: int
    """
    game   = get_game(chat_id)
    player = game["players"][user_id]

    if not player["alive"]:
        return {"result": "dead", "newly_revealed": 0, "lives_left": 0}

    if player["revealed"][row][col]:
        return {"result": "already", "newly_revealed": 0,
                "lives_left": player["lives"]}

    if player["flagged"][row][col]:
        return {"result": "already", "newly_revealed": 0,
                "lives_left": player["lives"]}

    # First tap — generate board now
    if player["board"] is None:
        init_player_board(chat_id, user_id, row, col)

    board = player["board"]

    if board[row][col] == -1:
        # Mine hit
        player["lives"] -= 1
        player["revealed"][row][col] = True

        if player["lives"] <= 0:
            player["alive"] = False
            # Reveal all mines for dead player
            for r in range(game["rows"]):
                for c in range(game["cols"]):
                    if board[r][c] == -1:
                        player["revealed"][r][c] = True

        return {"result": "mine", "newly_revealed": 1,
                "lives_left": player["lives"]}

    # Safe cell
    newly = _flood_fill(board, player["revealed"], player["flagged"], row, col)
    player["safe_count"] += newly

    # Check win
    if player["safe_count"] >= player["total_safe"]:
        return {"result": "win", "newly_revealed": newly,
                "lives_left": player["lives"]}

    return {"result": "safe", "newly_revealed": newly,
            "lives_left": player["lives"]}


def toggle_flag(chat_id: int, user_id: int, row: int, col: int) -> bool:
    """Returns True if flag was placed, False if removed."""
    game   = get_game(chat_id)
    player = game["players"][user_id]

    if player["revealed"][row][col]:
        return None  # can't flag revealed cell

    player["flagged"][row][col] = not player["flagged"][row][col]
    return player["flagged"][row][col]


def format_players(game: dict) -> str:
    lines = []
    for uid, p in game["players"].items():
        lives = "❤️" * p["lives"] + "🖤" * (MAX_LIVES - p["lives"])
        status = "💀" if not p["alive"] else "🟢"
        lines.append(f"  {status} {lives} <b>{p['name']}</b>  —  {p['safe_count']} safe")
    return "\n".join(lines) if lines else "  <i>No players~</i>"


def alive_players(game: dict) -> list:
    return [uid for uid, p in game["players"].items() if p["alive"]]


def is_game_over(game: dict) -> bool:
    """Game over when all players are dead or only 1 alive in rival mode."""
    alive = alive_players(game)
    if not alive:
        return True
    if game["mode"] == "rival" and len(alive) == 1 and len(game["players"]) > 1:
        return True
    return False


def get_winner(game: dict) -> Optional[int]:
    alive = alive_players(game)
    if not alive:
        # Winner = most safe squares among all
        all_p = game["players"]
        if not all_p:
            return None
        return max(all_p, key=lambda uid: all_p[uid]["safe_count"])
    if len(alive) == 1:
        return alive[0]
    # All alive — winner = most safe squares
    return max(alive, key=lambda uid: game["players"][uid]["safe_count"])


# ── Keyboard builders ─────────────────────────────────────

def join_buttons(mode: str = "rival") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💎 Join Game",  callback_data="ms_join"),
            InlineKeyboardButton("🚀 Start!",     callback_data="ms_start"),
        ],
        [
            InlineKeyboardButton("🟢 Easy",   callback_data="ms_diff_easy"),
            InlineKeyboardButton("🟡 Medium", callback_data="ms_diff_medium"),
            InlineKeyboardButton("🔴 Hard",   callback_data="ms_diff_hard"),
        ],
        [InlineKeyboardButton("❌ Cancel",    callback_data="ms_cancel")],
    ])


def board_buttons(chat_id: int, user_id: int,
                  flag_mode: bool = False) -> InlineKeyboardMarkup:
    game   = get_game(chat_id)
    player = game["players"][user_id]
    board  = player["board"]
    revealed = player["revealed"]
    flagged  = player["flagged"]
    rows, cols = game["rows"], game["cols"]

    rows_btns = []

    for r in range(rows):
        row_btns = []
        for c in range(cols):
            if flagged[r][c]:
                label = S.FLAG_EMOJI
                cb    = f"ms_unflag_{r}_{c}"
            elif not revealed[r][c]:
                label = S.HIDDEN_EMOJI
                cb    = f"ms_flag_{r}_{c}" if flag_mode else f"ms_tap_{r}_{c}"
            else:
                if board is None:
                    label = S.HIDDEN_EMOJI
                    cb    = f"ms_tap_{r}_{c}"
                elif board[r][c] == -1:
                    label = S.MINE_EMOJI
                    cb    = "ms_noop"
                else:
                    label = S.NUMBER_EMOJI.get(board[r][c], "　")
                    cb    = "ms_noop"

            row_btns.append(InlineKeyboardButton(label, callback_data=cb))
        rows_btns.append(row_btns)

    # Control row
    flag_btn_label = "🚩 Flag Mode ON" if flag_mode else "🚩 Flag Mode"
    flag_cb        = "ms_flagmode_off" if flag_mode else "ms_flagmode_on"
    rows_btns.append([
        InlineKeyboardButton(flag_btn_label, callback_data=flag_cb),
    ])

    return InlineKeyboardMarkup(rows_btns)


def spectate_board_buttons(chat_id: int, user_id: int) -> InlineKeyboardMarkup:
    """Read-only board for dead/spectating players."""
    game   = get_game(chat_id)
    player = game["players"].get(user_id)
    if not player or not player["board"]:
        return InlineKeyboardMarkup([[]])

    board    = player["board"]
    revealed = player["revealed"]
    flagged  = player["flagged"]
    rows, cols = game["rows"], game["cols"]

    rows_btns = []
    for r in range(rows):
        row_btns = []
        for c in range(cols):
            if flagged[r][c]:
                label = S.FLAG_EMOJI
            elif not revealed[r][c]:
                label = S.HIDDEN_EMOJI
            else:
                label = S.MINE_EMOJI if board[r][c] == -1 \
                    else S.NUMBER_EMOJI.get(board[r][c], "　")
            row_btns.append(InlineKeyboardButton(label, callback_data="ms_noop"))
        rows_btns.append(row_btns)

    return InlineKeyboardMarkup(rows_btns)