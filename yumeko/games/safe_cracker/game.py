# ==========================================================
#  Yumeko Games Bot — Safe Cracker Game Logic
#  Copyright (c) 2026 Jass  |  Version 2.0.0
# ==========================================================

import random
from datetime import datetime
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from yumeko.games.safe_cracker import strings as S

# ── Constants ─────────────────────────────────────────────
REWARD_COINS   = 70
REWARD_XP      = 35
GENIUS_BONUS   = 50   # cracked in ≤3 guesses
SHARP_BONUS    = 20   # cracked in ≤5 guesses
LOSER_XP       = 10
MIN_PLAYERS    = 1
MAX_PLAYERS    = 10
JOIN_TIMEOUT   = 60

active_games: dict[int, dict] = {}


# ── Code generation ───────────────────────────────────────

def _generate_code() -> list:
    """4-symbol code — symbols can repeat."""
    return [random.choice(S.SYMBOLS) for _ in range(S.CODE_LENGTH)]


def _evaluate_guess(code: list, guess: list) -> tuple[int, int]:
    """
    Returns (bulls, cows).
    bulls = correct symbol + correct position
    cows  = correct symbol + wrong position
    """
    bulls = sum(c == g for c, g in zip(code, guess))

    # Cows — count symbols in common minus bulls
    code_counts  = {}
    guess_counts = {}
    for i in range(S.CODE_LENGTH):
        if code[i] != guess[i]:
            code_counts[code[i]]   = code_counts.get(code[i], 0)   + 1
            guess_counts[guess[i]] = guess_counts.get(guess[i], 0) + 1

    cows = sum(min(code_counts.get(s, 0), guess_counts.get(s, 0))
               for s in set(guess_counts))

    return bulls, cows


# ── State ─────────────────────────────────────────────────

def create_game(chat_id: int, host_id: int, host_name: str):
    active_games[chat_id] = {
        "host_id":    host_id,
        "host_name":  host_name,
        "players":    {},
        "code":       _generate_code(),
        "status":     "joining",
        "winner_id":  None,
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

    game["players"][user.id] = {
        "name":         user.first_name or "Unknown",
        "guesses_left": S.MAX_GUESSES,
        "current_build": [],       # symbols tapped so far
        "history":      [],        # [(guess, bulls, cows), ...]
        "done":         False,     # cracked or out of guesses
        "won":          False,
        "guesses_used": 0,
    }
    return True, "ok"


def format_players(game: dict) -> str:
    lines = []
    for uid, p in game["players"].items():
        if p["won"]:
            status = "🏆"
        elif p["done"]:
            status = "💀"
        else:
            status = f"🔐 {p['guesses_left']}G"
        lines.append(f"  {status} <b>{p['name']}</b>")
    return "\n".join(lines) if lines else "  <i>No players~</i>"


def all_done(game: dict) -> bool:
    return all(p["done"] for p in game["players"].values())


def add_symbol(chat_id: int, user_id: int, symbol: str) -> bool:
    """Add symbol to current build. Returns True if added."""
    game   = get_game(chat_id)
    player = game["players"].get(user_id)
    if not player or player["done"]:
        return False
    if len(player["current_build"]) >= S.CODE_LENGTH:
        return False
    player["current_build"].append(symbol)
    return True


def remove_last(chat_id: int, user_id: int) -> bool:
    """Remove last symbol from build."""
    game   = get_game(chat_id)
    player = game["players"].get(user_id)
    if not player or not player["current_build"]:
        return False
    player["current_build"].pop()
    return True


def clear_build(chat_id: int, user_id: int):
    game = get_game(chat_id)
    if game and user_id in game["players"]:
        game["players"][user_id]["current_build"] = []


def submit_guess(chat_id: int, user_id: int) -> dict:
    """
    Submit current build as a guess.
    Returns dict: result, bulls, cows, guesses_left, won, eliminated
    """
    game   = get_game(chat_id)
    player = game["players"].get(user_id)

    if not player or player["done"]:
        return {"result": "done"}

    if len(player["current_build"]) < S.CODE_LENGTH:
        return {"result": "incomplete"}

    guess  = player["current_build"][:]
    code   = game["code"]
    bulls, cows = _evaluate_guess(code, guess)

    player["history"].append((guess, bulls, cows))
    player["guesses_used"] += 1
    player["guesses_left"] -= 1
    player["current_build"] = []

    if bulls == S.CODE_LENGTH:
        player["done"] = True
        player["won"]  = True
        game["winner_id"] = user_id
        return {
            "result":       "win",
            "bulls":        bulls,
            "cows":         cows,
            "guesses_used": player["guesses_used"],
        }

    if player["guesses_left"] <= 0:
        player["done"] = True
        return {
            "result":       "eliminated",
            "bulls":        bulls,
            "cows":         cows,
            "guesses_left": 0,
        }

    return {
        "result":       "feedback",
        "bulls":        bulls,
        "cows":         cows,
        "guesses_left": player["guesses_left"],
        "guess":        guess,
    }


# ── Keyboard builders ─────────────────────────────────────

def join_buttons() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔐 Join Game", callback_data="sc_join"),
            InlineKeyboardButton("🚀 Start!",    callback_data="sc_start"),
        ],
        [InlineKeyboardButton("❌ Cancel",       callback_data="sc_cancel")],
    ])


def panel_buttons(current_build: list) -> InlineKeyboardMarkup:
    """
    Full cracking panel:
    Row 1-2: symbol buttons (3 per row)
    Row 3:   current build display (read-only labels)
    Row 4:   ⌫ Delete  |  🗑 Clear  |  ✅ Submit
    """
    rows = []

    # Symbol buttons — 3 per row
    symbols = S.SYMBOLS
    for i in range(0, len(symbols), 3):
        row = []
        for sym in symbols[i:i+3]:
            row.append(InlineKeyboardButton(sym, callback_data=f"sc_sym_{sym}"))
        rows.append(row)

    # Current build display row
    build_display = []
    for i in range(S.CODE_LENGTH):
        label = current_build[i] if i < len(current_build) else "⬜"
        build_display.append(
            InlineKeyboardButton(label, callback_data="sc_noop")
        )
    rows.append(build_display)

    # Action row
    rows.append([
        InlineKeyboardButton("⌫ Delete",  callback_data="sc_delete"),
        InlineKeyboardButton("🗑 Clear",   callback_data="sc_clear"),
        InlineKeyboardButton("✅ Submit",  callback_data="sc_submit"),
    ])

    return InlineKeyboardMarkup(rows)


def done_panel_buttons() -> InlineKeyboardMarkup:
    """Shown when player is done (won or eliminated)."""
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🔐 Game Over for you~  ♡", callback_data="sc_noop"),
    ]])