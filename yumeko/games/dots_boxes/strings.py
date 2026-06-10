# ==========================================================
#  Yumeko Games Bot — Dots & Boxes Strings
#  Copyright (c) 2026 Jass
# ==========================================================

import random


ALREADY_RUNNING = "▪️ A Dots & Boxes game is already running in this group."
NO_GAME = "❌ No Dots & Boxes game is active."
ALREADY_JOINED = "✅ You're already inside this match."
GAME_FULL = "⚡ This board is full."
HOST_ONLY = "👑 Only the host can do that."
NOT_ENOUGH = "❌ Need at least 2 players."
NOT_PLAYER = "🚫 You're not part of this match."
NOT_YOUR_TURN = "⌛ Not your turn, darling~"
INVALID_LINE = "❌ That line is already drawn or invalid."
GAME_CANCELLED = (
    "<blockquote>🛑 <b>Dots & Boxes Cancelled</b></blockquote>\n\n"
    "<i>❝ The little dots return to silence~ ♡ ❞</i>"
)


def lobby_text(host_name, players_text, count, max_players):
    quotes = [
        "Every little line can steal a little kingdom. ♡",
        "Tiny dots. Tiny lines. Very dangerous intentions. ♡",
        "Draw carefully, darling. One line can gift your rival a box. ♡",
        "The board looks innocent. It is not. ♡",
    ]

    return (
        "<blockquote>▪️ <b>DOTS & BOXES</b></blockquote>\n\n"
        f"<i>❝ {random.choice(quotes)} ❞</i>\n\n"
        f"🎭 <b>Host:</b> {host_name}\n\n"
        "▪️ Draw lines between dots.\n"
        "📦 Complete a box to claim it.\n"
        "🎁 Completing a box gives an extra turn.\n"
        "🏆 Most boxes wins.\n\n"
        "<blockquote>\n"
        "📐 <b>Box Rule</b>\n\n"
        "If your line closes a square,\n"
        "that square becomes yours.\n"
        "</blockquote>\n\n"
        f"👥 <b>Players ({count}/{max_players})</b>\n\n"
        f"{players_text}\n\n"
        "⏳ <i>The dots are waiting to be connected...</i>\n\n"
        "♡ Yumeko loves watching small choices become traps."
    )


def arena_text(board, current_name, current_mark, round_no):
    return (
        "<blockquote>▪️ <b>DOTS & BOXES</b></blockquote>\n\n"
        f"🎯 Turn: {current_mark} <b>{current_name}</b>\n"
        f"🔢 Round: <b>{round_no}</b>\n\n"
        f"<pre>{board}</pre>\n\n"
        "<i>Choose a line below, darling~</i>"
    )


def move_text(player_name, mark, line_type, row, col, completed):
    kind = "horizontal" if line_type == "h" else "vertical"

    text = (
        "<blockquote>✏️ <b>LINE DRAWN</b></blockquote>\n\n"
        f"{mark} <b>{player_name}</b> drew a <b>{kind}</b> line.\n"
        f"📍 Position: <b>R{row + 1} C{col + 1}</b>\n\n"
    )

    if completed:
        text += (
            "<blockquote>📦 <b>BOX CLAIMED!</b></blockquote>\n\n"
            f"Claimed boxes: <b>{len(completed)}</b>\n"
            "Extra turn granted~ ♡\n\n"
        )
    else:
        text += random.choice([
            "The board shifts quietly...\n\n",
            "A careful little move~\n\n",
            "No box yet. How tense~ ♡\n\n",
        ])

    return text


def winner_text(winner_name, winner_mark, scoreboard, coins, xp):
    return (
        "<blockquote>🏆 <b>DOTS & BOXES CHAMPION</b></blockquote>\n\n"
        f"👑 Winner: {winner_mark} <b>{winner_name}</b>\n\n"
        f"🪙 +<b>{coins}</b> Coins\n"
        f"⭐ +<b>{xp}</b> XP\n\n"
        "<blockquote>📊 <b>Final Scoreboard</b></blockquote>\n\n"
        f"{scoreboard}\n\n"
        "<i>❝ Tiny boxes. Beautiful domination. ♡ ❞</i>"
    )


def draw_text(scoreboard, xp):
    return (
        "<blockquote>🤝 <b>DOTS & BOXES DRAW</b></blockquote>\n\n"
        "No one owned enough of the board to claim the throne.\n\n"
        f"⭐ Everyone gets <b>{xp}</b> XP.\n\n"
        "<blockquote>📊 <b>Final Scoreboard</b></blockquote>\n\n"
        f"{scoreboard}"
    )


def rules_text():
    return (
        "<blockquote>📖 <b>Dots & Boxes Rules</b></blockquote>\n\n"
        "• Players take turns drawing one line.\n"
        "• Lines can be horizontal or vertical.\n"
        "• If your line completes a square, you claim that box.\n"
        "• Claimed boxes give an extra turn.\n"
        "• When all lines are drawn, the player with most boxes wins.\n\n"
        "🏆 Rewards:\n"
        "🪙 Winner Coins\n"
        "⭐ Winner XP"
    )