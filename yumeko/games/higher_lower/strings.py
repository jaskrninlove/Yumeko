# ==========================================================
#  Yumeko Games Bot — Higher or Lower Strings
#  Copyright (c) 2026 Jass  |  Version 2.0.0
# ==========================================================

import random

# ── Card display ──────────────────────────────────────────

SUITS = ["♠️", "♥️", "♦️", "♣️"]
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
RANK_VALUES = {
    "A": 1, "2": 2, "3": 3, "4": 4, "5": 5,
    "6": 6, "7": 7, "8": 8, "9": 9, "10": 10,
    "J": 11, "Q": 12, "K": 13,
}

def card_display(rank: str, suit: str) -> str:
    return f"<b>{rank}{suit}</b>"


# ── Lobby ─────────────────────────────────────────────────

def lobby_text(host: str, player_list: str, count: int, timeout: int) -> str:
    openers = [
        "Higher or lower~  Such a simple question~  With such devastating consequences~  ♡",
        "Ahahaha~  Every card is a gamble~  Every guess is a risk~  ♡",
        "The deck doesn't care about your feelings~  Only your instincts~  ♡",
        "One card~  Two choices~  Everything on the line~  ♡",
        "Streaks multiply your reward~  But one wrong guess ends it all~  ♡",
    ]
    return (
        f"<blockquote>🃏 <b>HIGHER OR LOWER</b></blockquote>\n\n"
        f"<i>❝ {random.choice(openers)} ❞</i>\n\n"
        f"🎴 Host: <b>{host}</b>\n\n"
        f"<b>How It Works:</b>\n"
        f"  ◈ Yumeko reveals a card\n"
        f"  ◈ Tap <b>⬆️ Higher</b> or <b>⬇️ Lower</b>\n"
        f"  ◈ Correct — your streak grows~  ♡\n"
        f"  ◈ Wrong — you lose a life\n"
        f"  ◈ <b>3 lives</b> each~  Lose all 3 — eliminated\n"
        f"  ◈ <b>Streak multiplier</b> — longer streak = more coins\n"
        f"  ◈ <b>10 rounds</b> — most points wins\n\n"
        f"🏆 <b>Streak Multipliers:</b>\n"
        f"  3 correct → 1.5×  ·  5 correct → 2×  ·  8 correct → 3×\n\n"
        f"👥 <b>Players ({count}):</b>\n{player_list}\n\n"
        f"⏳ <i>Auto-starts in {timeout}s...</i>"
    )

def lobby_updated(host: str, player_list: str, count: int) -> str:
    lines = [
        "Another gambler joins the table~  ♡",
        "Ahahaha~  The deck grows more interesting~  ♡",
        "More players~  More tension~  ♡",
    ]
    return (
        f"<blockquote>🃏 <b>HIGHER OR LOWER</b></blockquote>\n\n"
        f"<i>❝ {random.choice(lines)} ❞</i>\n\n"
        f"🎴 Host: <b>{host}</b>\n\n"
        f"👥 <b>Players ({count}):</b>\n{player_list}\n\n"
        f"<i>Waiting for host to deal the first card...</i>"
    )


# ── Round ─────────────────────────────────────────────────

def round_text(round_num: int, total: int, rank: str, suit: str,
               scoreboard: str, seconds: int) -> str:
    taunts = [
        "Higher~?  Lower~?  ♡  Trust your gut.",
        "Ahahaha~  What does the next card hold~?  ♡",
        "The deck knows~  Do you~?  ♡",
        "One tap~  One fate~  ♡",
        "Feel the card~  ♡  Let instinct decide.",
        "Hesitation costs you nothing~  A wrong guess costs everything~  ♡",
    ]
    return (
        f"<blockquote>🃏 <b>Round {round_num} / {total}</b></blockquote>\n\n"
        f"<i>❝ {random.choice(taunts)} ❞</i>\n\n"
        f"Current Card:  {card_display(rank, suit)}\n\n"
        f"Is the next card <b>Higher</b> or <b>Lower</b>~?\n\n"
        f"📊 <b>Standings:</b>\n{scoreboard}\n\n"
        f"⏱️ <b>{seconds}s</b> to decide~"
    )


# ── Round result ──────────────────────────────────────────

def result_text(prev_rank: str, prev_suit: str,
                new_rank: str, new_suit: str,
                correct_direction: str,
                winners: list, losers: list,
                round_num: int, total: int) -> str:
    direction_emoji = "⬆️" if correct_direction == "higher" else ("⬇️" if correct_direction == "lower" else "↔️")

    winner_lines = "\n".join(f"  ✅ <b>{n}</b>  (streak ×{s})" for n, s in winners) if winners else "  <i>Nobody got it~</i>"
    loser_lines  = "\n".join(f"  ❌ <b>{n}</b>  -{l} life" for n, l in losers)   if losers  else ""

    reveals = [
        f"The card was {card_display(new_rank, new_suit)}~  {direction_emoji}  ♡",
        f"Ahahaha~  {card_display(new_rank, new_suit)}~  {direction_emoji}~  ♡",
        f"Next card: {card_display(new_rank, new_suit)}~  {direction_emoji}~  ♡",
    ]
    return (
        f"<blockquote>🃏 <b>Round {round_num} / {total} — Result</b></blockquote>\n\n"
        f"<i>❝ {random.choice(reveals)} ❞</i>\n\n"
        f"{card_display(prev_rank, prev_suit)} → {card_display(new_rank, new_suit)}\n\n"
        f"<b>Correct:</b>\n{winner_lines}\n"
        + (f"\n<b>Wrong:</b>\n{loser_lines}" if loser_lines else "")
    )


def tie_text(prev_rank: str, new_rank: str) -> str:
    return (
        f"<i>❝ Ahahaha~  Same value~  {prev_rank} → {new_rank}~  "
        f"Nobody wins or loses this round~  ♡ ❞</i>"
    )


# ── Streak announcements ──────────────────────────────────

def streak_announcement(name: str, streak: int, multiplier: float) -> str:
    if streak == 3:
        return f"🔥 <b>{name}</b> is on a <b>{streak}-streak</b>~  ×{multiplier} multiplier~  ♡"
    if streak == 5:
        return f"🔥🔥 <b>{name}</b>~  <b>{streak} in a row</b>~  ×{multiplier}~  Ahahaha~  ♡"
    if streak == 8:
        return f"💀 <b>{name}</b>~  <b>{streak}-streak</b>~  ×{multiplier}~  UNSTOPPABLE~  ♡"
    return ""


# ── Elimination ───────────────────────────────────────────

def eliminated_text(name: str, streak: int) -> str:
    msgs = [
        f"💀 <b>{name}</b> ran out of lives~  ♡  Best streak: <b>{streak}</b>",
        f"💀 Ahahaha~  <b>{name}</b> is gone~  They lasted <b>{streak}</b> correct in a row~  ♡",
        f"💀 <b>{name}</b>~  The deck finally broke you~  ♡  Streak: <b>{streak}</b>",
    ]
    return random.choice(msgs)


# ── Scoreboard ────────────────────────────────────────────

def scoreboard_text(players: dict) -> str:
    sorted_p = sorted(players.items(), key=lambda x: x[1]["points"], reverse=True)
    medals   = ["🥇", "🥈", "🥉"] + ["🔹"] * 20
    lines    = []
    for i, (uid, p) in enumerate(sorted_p):
        lives    = "❤️" * p["lives"] + "🖤" * (3 - p["lives"])
        streak   = f"  🔥×{p['streak']}" if p["streak"] >= 3 else ""
        status   = "💀" if not p["alive"] else medals[i]
        lines.append(
            f"  {status} <b>{p['name']}</b>  —  {p['points']} pts  {lives}{streak}"
        )
    return "\n".join(lines) if lines else "  <i>No players~</i>"


# ── Victory ───────────────────────────────────────────────

def victory_text(winner: str, points: int, best_streak: int,
                 final_board: str, coins: int, xp: int, loser_xp: int) -> str:
    closes = [
        f"<b>{winner}</b>~  The cards bowed to you~  ♡  Magnificent.",
        f"Ahahaha~  <b>{winner}</b> read every card~  ♡  Incredible.",
        f"<b>{winner}</b>~  Instinct over logic~  ♡  That's the Yumeko way.",
        f"<b>{winner}</b>~  The deck never fooled you~  ♡",
    ]
    return (
        f"<blockquote>🏆 <b>HIGHER OR LOWER — OVER!</b></blockquote>\n\n"
        f"<i>❝ {random.choice(closes)} ❞</i>\n\n"
        f"👑 Champion: <b>{winner}</b>\n"
        f"📊 Points: <b>{points}</b>\n"
        f"🔥 Best Streak: <b>{best_streak}</b>\n\n"
        f"<b>Final Standings:</b>\n{final_board}\n\n"
        f"💰 +<b>{coins}</b> coins  ·  ✨ +<b>{xp}</b> XP\n"
        f"<i>Others: +{loser_xp} XP for playing~  ♡</i>"
    )


def no_winner_text() -> str:
    return (
        f"<blockquote>😴 <b>No Winner</b></blockquote>\n\n"
        f"<i>❝ Everyone lost their lives~  ♡  The deck wins tonight. ❞</i>"
    )


# ── Misc ──────────────────────────────────────────────────

ALREADY_RUNNING = "🃏 <i>A Higher or Lower game is already running~  Join it!</i>"
NOT_ENOUGH      = "<i>❝ Need at least <b>2 players</b> to start~  ♡ ❞</i>"
GAME_CANCELLED  = (
    "<blockquote>❌ <b>Game Cancelled</b></blockquote>\n\n"
    "<i>❝ The cards go undealt~  How anticlimactic~  ♡ ❞</i>"
)
ALREADY_JOINED  = "<i>❝ You're already at the table~  ♡ ❞</i>"
GAME_FULL       = "<i>❝ Table is full~  20 players max~  ♡ ❞</i>"
HOST_ONLY       = "<i>❝ Hosts only~  ♡ ❞</i>"
NOT_IN_GAME     = "<i>❝ You're not in this game~  ♡ ❞</i>"
ALREADY_VOTED   = "<i>❝ Already chose~  ♡  Wait for the reveal~</i>"
ALREADY_DEAD    = "<i>❝ You're already eliminated~  Watch and learn~  ♡ ❞</i>"
ROUND_CLOSED    = "<i>❝ Round already closed~  ♡ ❞</i>"
GROUPS_ONLY     = "<i>❝ This game belongs in groups~  ♡ ❞</i>"