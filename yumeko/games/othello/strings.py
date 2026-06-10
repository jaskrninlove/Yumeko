# ==========================================================
#  Yumeko Games Bot — Othello / Reversi Strings
#  Copyright (c) 2026 Jass
# ==========================================================

import random


ALREADY_RUNNING = (
    "♟ <i>An Othello match is already running in this group, darling~</i>"
)

NO_GAME = (
    "♟ <i>No Othello match is currently active.</i>"
)

ALREADY_JOINED = (
    "♟ <i>You're already seated at the board, darling~</i>"
)

GAME_FULL = (
    "♟ <i>The board only welcomes two players.</i>"
)

HOST_ONLY = (
    "👑 <i>Only the host may do that.</i>"
)

NOT_ENOUGH = (
    "♟ <i>Need at least <b>2 players</b> to begin.</i>"
)

NOT_PLAYER = (
    "♟ <i>You are not part of this match.</i>"
)

NOT_YOUR_TURN = (
    "⏳ <i>Patience, darling~ It's not your turn.</i>"
)

INVALID_MOVE = (
    "❌ <i>That move captures nothing. Try another square.</i>"
)

GAME_CANCELLED = (
    "<blockquote>🛑 <b>Othello Cancelled</b></blockquote>\n\n"
    "<i>❝ The pieces return to silence. ♡ ❞</i>"
)


# ----------------------------------------------------------
# Lobby
# ----------------------------------------------------------

def lobby_text(host_name, players_text, count, max_players):
    quotes = [
        "Every piece you place changes the entire board. ♡",
        "A single move can reverse everything. ♡",
        "Black and white. Simple. Yet endlessly cruel. ♡",
        "The board remembers every mistake. ♡",
    ]

    return (
        "<blockquote>♟ <b>OTHELLO / REVERSI</b></blockquote>\n\n"
        f"<i>❝ {random.choice(quotes)} ❞</i>\n\n"
        f"🎭 Host: <b>{host_name}</b>\n\n"
        "<b>How It Works</b>\n"
        "• Surround enemy pieces\n"
        "• Flip them to your color\n"
        "• Control more squares than your rival\n"
        "• Most pieces at the end wins\n\n"
        "<blockquote>"
        "⚫ First Player = Black\n"
        "⚪ Second Player = White\n"
        "</blockquote>\n\n"
        f"👥 <b>Players ({count}/{max_players})</b>\n\n"
        f"{players_text}\n\n"
        "⏳ <i>Waiting for the duel to begin...</i>"
    )


# ----------------------------------------------------------
# Arena
# ----------------------------------------------------------

def arena_text(
    current_name,
    current_piece,
    board,
    black_count,
    white_count,
):
    return (
        "<blockquote>♟ <b>OTHELLO</b></blockquote>\n\n"
        f"🎯 Turn: <b>{current_name}</b> {current_piece}\n\n"
        f"⚫ Black: <b>{black_count}</b>\n"
        f"⚪ White: <b>{white_count}</b>\n\n"
        f"<pre>{board}</pre>\n\n"
        "<i>Choose a square, darling~</i>"
    )


# ----------------------------------------------------------
# Move
# ----------------------------------------------------------

def move_text(
    player_name,
    piece,
    row,
    col,
    flips,
):
    messages = [
        "Beautiful~ ♡",
        "A clever reversal~ ♡",
        "The board bends to your will~ ♡",
        "Elegant. Ruthless. Perfect. ♡",
    ]

    return (
        "<blockquote>♟ <b>MOVE PLAYED</b></blockquote>\n\n"
        f"{piece} <b>{player_name}</b> placed at "
        f"<b>{row + 1},{col + 1}</b>\n\n"
        f"🔄 Flipped: <b>{flips}</b> pieces\n\n"
        f"<i>❝ {random.choice(messages)} ❞</i>"
    )


def skip_turn_text(player_name):
    return (
        "<blockquote>⏭ <b>TURN SKIPPED</b></blockquote>\n\n"
        f"<b>{player_name}</b> has no legal moves.\n\n"
        "<i>The board refuses to cooperate. ♡</i>"
    )


# ----------------------------------------------------------
# Rules
# ----------------------------------------------------------

def rules_text():
    return (
        "<blockquote>📖 <b>Othello Rules</b></blockquote>\n\n"
        "♟ Two players.\n\n"
        "⚫ Black moves first.\n"
        "⚪ White moves second.\n\n"
        "A move is valid only if it traps enemy pieces between your pieces.\n\n"
        "All trapped pieces flip to your color.\n\n"
        "If a player has no valid move, their turn is skipped.\n\n"
        "When the board fills up (or neither player can move), the player with more pieces wins.\n\n"
        "🏆 Winner receives Coins + XP."
    )


# ----------------------------------------------------------
# Victory
# ----------------------------------------------------------

def winner_text(
    winner_name,
    winner_piece,
    scoreboard,
    black_count,
    white_count,
    coins,
    xp,
):
    endings = [
        "The board belongs to you tonight. ♡",
        "A flawless display of control. ♡",
        "Even the pieces obeyed your wishes. ♡",
        "A beautiful victory, darling~ ♡",
    ]

    return (
        "<blockquote>🏆 <b>OTHELLO COMPLETE</b></blockquote>\n\n"
        f"👑 Winner: <b>{winner_name}</b> {winner_piece}\n\n"
        f"⚫ Black: <b>{black_count}</b>\n"
        f"⚪ White: <b>{white_count}</b>\n\n"
        "<b>Final Standings</b>\n"
        f"{scoreboard}\n\n"
        f"💰 +<b>{coins}</b> Coins\n"
        f"✨ +<b>{xp}</b> XP\n\n"
        f"<i>❝ {random.choice(endings)} ❞</i>"
    )


def draw_text(
    scoreboard,
    black_count,
    white_count,
):
    return (
        "<blockquote>🤝 <b>DRAW</b></blockquote>\n\n"
        "Neither side could dominate the board.\n\n"
        f"⚫ Black: <b>{black_count}</b>\n"
        f"⚪ White: <b>{white_count}</b>\n\n"
        f"{scoreboard}\n\n"
        "<i>❝ Balance is sometimes the cruelest outcome. ♡ ❞</i>"
    )