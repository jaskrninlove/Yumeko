# ==========================================================
#  Yumeko Games Bot — Connect Four Strings
#  Copyright (c) 2026 Jass
# ==========================================================

ALREADY_RUNNING = (
    "🎮 A Connect Four match is already running in this group."
)

NOT_ENOUGH = (
    "❌ Not enough players joined.\n\n"
    "Connect Four requires 2 players."
)

GAME_CANCELLED = (
    "<blockquote>🛑 <b>Match Cancelled</b></blockquote>\n\n"
    "The board has been cleared, darling~ ♡"
)

GAME_FULL = (
    "⚡ This match already has 2 players."
)

ALREADY_JOINED = (
    "✅ You're already in the match."
)

HOST_ONLY = (
    "👑 Only the host can do that."
)

NOT_YOUR_TURN = (
    "⌛ It's not your turn."
)

COLUMN_FULL = (
    "🚫 That column is already full."
)

DRAW_GAME = (
    "<blockquote>🤝 <b>Draw Game</b></blockquote>\n\n"
    "The board is full.\n"
    "No winner this time, darling~ ♡"
)


def lobby_text(host_name, players_text, count, timeout):
    return (
        "<blockquote>🔴🟡 <b>Connect Four Lobby</b></blockquote>\n\n"
        f"👑 Host: <b>{host_name}</b>\n"
        f"👥 Players: <b>{count}/2</b>\n\n"
        f"{players_text}\n\n"
        f"⏳ Match starts in <b>{timeout}s</b>\n\n"
        "<i>First player to connect four pieces wins~ ♡</i>"
    )


def game_started_text(players_text):
    return (
        "<blockquote>🎮 <b>Connect Four Started</b></blockquote>\n\n"
        f"{players_text}\n\n"
        "<i>Let the battle begin~ ♡</i>"
    )


def turn_text(player_name, piece):
    return (
        f"🎯 Turn: {piece} <b>{player_name}</b>\n\n"
        "Choose a column below."
    )


def winner_text(player_name, piece):
    return (
        "<blockquote>🏆 <b>Winner</b></blockquote>\n\n"
        f"{piece} <b>{player_name}</b>\n\n"
        "connected four pieces and claimed victory~ ♡"
    )


def move_text(player_name, piece, column):
    return (
        f"{piece} <b>{player_name}</b>\n"
        f"dropped a piece into column <b>{column}</b>."
    )