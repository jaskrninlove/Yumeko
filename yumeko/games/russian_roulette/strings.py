# ==========================================================
#  Yumeko Games Bot — Russian Roulette Strings
#  Copyright (c) 2026 Jass
# ==========================================================

ALREADY_RUNNING = "🔫 A Russian Roulette game is already running."
NO_GAME = "❌ No Russian Roulette game is active."
ALREADY_JOINED = "✅ You're already sitting at the table."
GAME_FULL = "⚡ The table is full."
HOST_ONLY = "👑 Only the host can do that."
NOT_ENOUGH = "❌ Need at least 2 players."
NOT_PLAYER = "🚫 You're not part of this game."
NOT_YOUR_TURN = "⌛ It's not your turn."
ALREADY_DEAD = "💀 You're already dead."
GAME_CANCELLED = (
    "<blockquote>🛑 <b>Russian Roulette Cancelled</b></blockquote>\n\n"
    "The revolver returns to Yumeko's pocket~ ♡"
)


def lobby_text(host_name, players_text, count, max_players):
    return (
        "<blockquote>🔫 <b>Russian Roulette</b></blockquote>\n\n"
        f"👑 Host: <b>{host_name}</b>\n"
        f"👥 Players: <b>{count}/{max_players}</b>\n\n"
        f"{players_text}\n\n"
        "One bullet.\n"
        "One revolver.\n"
        "One survivor.\n\n"
        "<i>❝ Let's see whose luck breaks first~ ♡ ❞</i>"
    )


def arena_text(current_name, round_no, alive_count):
    return (
        "<blockquote>🔫 <b>Russian Roulette</b></blockquote>\n\n"
        f"🎯 Turn: <b>{current_name}</b>\n"
        f"🔢 Round: <b>{round_no}</b>\n"
        f"🟢 Alive: <b>{alive_count}</b>\n\n"
        "<i>❝ Pull the trigger if you dare... ♡ ❞</i>"
    )


def safe_text(player_name, chamber):
    return (
        "<blockquote>😮 <b>CLICK...</b></blockquote>\n\n"
        f"<b>{player_name}</b> survived.\n\n"
        f"🔫 Chamber: <b>{chamber}/6</b>\n\n"
        "<i>Fate isn't finished with you yet~ ♡</i>"
    )


def bang_text(player_name):
    return (
        "<blockquote>💥 <b>BANG!</b></blockquote>\n\n"
        f"<b>{player_name}</b> has been eliminated.\n\n"
        "💀 The table grows quieter..."
    )


def reload_text():
    return (
        "🔄 <b>Revolver Reloaded</b>\n\n"
        "A fresh bullet hides somewhere inside..."
    )


def winner_text(winner_name, scoreboard, coins, xp):
    return (
        "<blockquote>🏆 <b>Russian Roulette Champion</b></blockquote>\n\n"
        f"👑 Winner: <b>{winner_name}</b>\n\n"
        f"🪙 +<b>{coins}</b> Coins\n"
        f"⭐ +<b>{xp}</b> XP\n\n"
        "<blockquote>📊 <b>Final Scoreboard</b></blockquote>\n\n"
        f"{scoreboard}\n\n"
        "<i>❝ Luck smiled upon you today, darling~ ♡ ❞</i>"
    )


def no_winner_text():
    return (
        "<blockquote>💀 <b>No Winner</b></blockquote>\n\n"
        "Everyone lost to fate..."
    )


def rules_text():
    return (
        "<blockquote>📖 <b>Russian Roulette Rules</b></blockquote>\n\n"
        "• Join the lobby.\n"
        "• Host starts the game.\n"
        "• Players take turns pulling the trigger.\n"
        "• If the chamber is empty, you survive.\n"
        "• If the bullet fires, you're eliminated.\n"
        "• Revolver reloads after every death.\n"
        "• Last player alive wins.\n\n"
        "🏆 Rewards:\n"
        "🪙 Winner Coins\n"
        "⭐ Winner XP\n"
    )


def scoreboard_text(scores):
    lines = []

    for idx, player in enumerate(scores, 1):
        lines.append(
            f"{idx}. {player['status']} "
            f"<b>{player['name']}</b> "
            f"(😮 {player['survived']} survived)"
        )

    return "\n".join(lines)