# ==========================================================
#  Yumeko Games Bot — Higher or Lower Game Logic
#  Copyright (c) 2026 Jass  |  Version 2.0.0
# ==========================================================

import random
from datetime import datetime
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from yumeko.games.higher_lower import strings as S

# ── Constants ─────────────────────────────────────────────
REWARD_COINS  = 55
REWARD_XP     = 25
LOSER_XP      = 10
MIN_PLAYERS   = 2
MAX_PLAYERS   = 20
JOIN_TIMEOUT  = 60
TOTAL_ROUNDS  = 10
ROUND_TIMEOUT = 15
MAX_LIVES     = 3

# Streak multipliers  (streak_threshold → multiplier)
STREAK_MULTIPLIERS = [(8, 3.0), (5, 2.0), (3, 1.5), (0, 1.0)]

active_games: dict[int, dict] = {}


# ── Deck helpers ──────────────────────────────────────────

def _new_deck() -> list[tuple]:
    """Returns shuffled deck as (rank, suit, value) tuples."""
    deck = []
    for suit in S.SUITS:
        for rank, val in S.RANK_VALUES.items():
            deck.append((rank, suit, val))
    random.shuffle(deck)
    return deck


def _draw(game: dict) -> tuple:
    """Draw next card, reshuffle if empty."""
    if not game["deck"]:
        game["deck"] = _new_deck()
    return game["deck"].pop()


def _get_multiplier(streak: int) -> float:
    for threshold, mult in STREAK_MULTIPLIERS:
        if streak >= threshold:
            return mult
    return 1.0


# ── State ─────────────────────────────────────────────────

def create_game(chat_id: int, host_id: int, host_name: str):
    deck = _new_deck()
    first_card = deck.pop()
    active_games[chat_id] = {
        "host_id":    host_id,
        "host_name":  host_name,
        "players":    {},
        "status":     "joining",
        "deck":       deck,
        "current_card": first_card,    # (rank, suit, value)
        "next_card":    None,
        "round":      0,
        "round_open": False,
        "votes":      {},              # user_id → "higher" | "lower"
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
        "name":        user.first_name or "Unknown",
        "lives":       MAX_LIVES,
        "alive":       True,
        "streak":      0,
        "best_streak": 0,
        "points":      0,
    }
    return True, "ok"


def alive_players(game: dict) -> list:
    return [uid for uid, p in game["players"].items() if p["alive"]]


def format_players(game: dict) -> str:
    lines = []
    for uid, p in game["players"].items():
        lives  = "❤️" * p["lives"] + "🖤" * (MAX_LIVES - p["lives"])
        status = "💀" if not p["alive"] else "🃏"
        lines.append(f"  {status} {lives} <b>{p['name']}</b>  —  {p['points']} pts")
    return "\n".join(lines) if lines else "  <i>No players~</i>"


# ── Keyboard builders ─────────────────────────────────────

def join_buttons() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🃏 Join Game",  callback_data="hl_join"),
            InlineKeyboardButton("🚀 Start!",     callback_data="hl_start"),
        ],
        [InlineKeyboardButton("❌ Cancel",        callback_data="hl_cancel")],
    ])


def vote_buttons() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⬆️ Higher",  callback_data="hl_vote_higher"),
            InlineKeyboardButton("⬇️ Lower",   callback_data="hl_vote_lower"),
        ],
    ])


def vote_buttons_voted(choice: str) -> InlineKeyboardMarkup:
    """Show which button the player already tapped."""
    higher_label = "✅ Higher" if choice == "higher" else "⬆️ Higher"
    lower_label  = "✅ Lower"  if choice == "lower"  else "⬇️ Lower"
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(higher_label, callback_data="hl_already"),
            InlineKeyboardButton(lower_label,  callback_data="hl_already"),
        ],
    ])


# ── Round resolution ──────────────────────────────────────

def resolve_round(game: dict) -> dict:
    """
    Evaluate votes against the next card.
    Returns dict with winners, losers, tie, correct_direction.
    """
    curr_val = game["current_card"][2]
    next_val = game["next_card"][2]

    if next_val > curr_val:
        correct = "higher"
    elif next_val < curr_val:
        correct = "lower"
    else:
        correct = "tie"

    winners = []   # (name, multiplier)
    losers  = []   # (name, lives_left)
    streak_announcements = []

    for uid, p in game["players"].items():
        if not p["alive"]:
            continue

        vote = game["votes"].get(uid)

        if correct == "tie":
            # Nobody wins or loses on a tie
            continue

        if vote == correct:
            p["streak"] += 1
            p["best_streak"] = max(p["best_streak"], p["streak"])
            mult   = _get_multiplier(p["streak"])
            points = int(10 * mult)
            p["points"] += points
            winners.append((p["name"], mult))

            # Streak milestone
            ann = S.streak_announcement(p["name"], p["streak"], mult)
            if ann:
                streak_announcements.append(ann)

        elif vote is not None:
            # Wrong guess
            p["streak"] = 0
            p["lives"]  -= 1
            if p["lives"] <= 0:
                p["alive"] = False
            losers.append((p["name"], 1))

        else:
            # No vote = wrong
            p["streak"] = 0
            p["lives"]  -= 1
            if p["lives"] <= 0:
                p["alive"] = False
            losers.append((p["name"], 1))

    return {
        "correct":               correct,
        "winners":               winners,
        "losers":                losers,
        "streak_announcements":  streak_announcements,
        "is_tie":                correct == "tie",
    }