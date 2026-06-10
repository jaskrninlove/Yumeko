# ==========================================================
#  Yumeko Games Bot — Gomoku Strings
#  Copyright (c) 2026 Jass
# ==========================================================

ALREADY_RUNNING = "⚫ A Gomoku match is already running in this group."
NO_GAME = "❌ No Gomoku match is active."
ALREADY_JOINED = "✅ You're already sitting at this board."
GAME_FULL = "⚡ Gomoku only supports 2 players."
HOST_ONLY = "👑 Only the host can do that."
NOT_ENOUGH = "❌ Need 2 players to begin."
NOT_PLAYER = "🚫 You're not part of this match."
NOT_YOUR_TURN = "⌛ Not your turn, darling~"
OCCUPIED = "🚫 That spot is already taken."
GAME_CANCELLED = (
    "<blockquote>🛑 <b>Gomoku Cancelled</b></blockquote>\n\n"
    "The stones return to silence~ ♡"
)


def lobby_text(host_name, players_text, count, max_players):
    return (
        "<blockquote>⚫ <b>GOMOKU</b></blockquote>\n\n"
        "<i>❝ Five stones.\n"
        "One perfect line.\n"
        "One beautiful victory. ♡ ❞</i>\n\n"
        f"🎭 <b>Host:</b> {host_name}\n\n"
        "⚫ Black versus White.\n"
        "♟ Every move matters.\n"
        "🏆 Connect five before your rival.\n\n"
        "<blockquote>\n"
        "🀄 <b>Ancient Board</b>\n\n"
        "Horizontal.\n"
        "Vertical.\n"
        "Diagonal.\n\n"
        "No luck. Only strategy.\n"
        "</blockquote>\n\n"
        f"👥 <b>Players ({count}/{max_players})</b>\n\n"
        f"{players_text}\n\n"
        "⏳ <i>The stones await their masters...</i>\n\n"
        "♡ Yumeko watches the board."
    )


def arena_text(board, current_name, current_stone):
    return (
        "<blockquote>⚫ <b>GOMOKU</b></blockquote>\n\n"
        f"🎯 Turn: {current_stone} <b>{current_name}</b>\n\n"
        f"<pre>{board}</pre>\n\n"
        "<i>Place your stone carefully. Five in a row wins~</i>"
    )


def move_text(player_name, stone, row, col):
    return (
        f"{stone} <b>{player_name}</b> placed a stone at "
        f"<b>R{row + 1} C{col + 1}</b>.\n\n"
    )


def winner_text(winner_name, stone, board, scoreboard, coins, xp):
    return (
        "<blockquote>🏆 <b>GOMOKU VICTORY</b></blockquote>\n\n"
        f"👑 Winner: {stone} <b>{winner_name}</b>\n\n"
        f"<pre>{board}</pre>\n\n"
        f"🪙 +<b>{coins}</b> Coins\n"
        f"⭐ +<b>{xp}</b> XP\n\n"
        "<blockquote>📊 <b>Final Scoreboard</b></blockquote>\n\n"
        f"{scoreboard}\n\n"
        "<i>❝ A perfect line. A perfect gamble. ♡ ❞</i>"
    )


def draw_text(board, scoreboard):
    return (
        "<blockquote>🤝 <b>GOMOKU DRAW</b></blockquote>\n\n"
        "The board is full, yet no perfect line was born.\n\n"
        f"<pre>{board}</pre>\n\n"
        "<blockquote>📊 <b>Final Scoreboard</b></blockquote>\n\n"
        f"{scoreboard}"
    )


def rules_text():
    return (
        "<blockquote>📖 <b>Gomoku Rules</b></blockquote>\n\n"
        "• Gomoku is a 2-player strategy game.\n"
        "• Black moves first.\n"
        "• Players place stones on empty cells.\n"
        "• First player to connect 5 stones wins.\n"
        "• Lines can be horizontal, vertical, or diagonal.\n"
        "• If the board fills with no winner, it is a draw.\n\n"
        "🏆 Rewards:\n"
        "🪙 Winner Coins\n"
        "⭐ Winner XP\n"
    )