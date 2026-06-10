# ==========================================================
#  Yumeko Games Bot — Poison Candy Strings
#  Copyright (c) 2026 Jass
# ==========================================================

ALREADY_RUNNING = "🍬 A Poison Candy game is already running in this group."
NO_GAME = "❌ No Poison Candy game is running."
ALREADY_JOINED = "✅ You're already inside this candy trap."
GAME_FULL = "⚡ This candy table is full."
HOST_ONLY = "👑 Only the host can do that."
NOT_ENOUGH = "❌ Need at least 2 players to begin."
NOT_PLAYER = "🚫 You're not part of this game."
NOT_YOUR_TURN = "⌛ Not your turn, darling~"
CELL_PICKED = "🍬 This candy was already picked."
POISON_ALREADY_SET = "🔐 You already placed your poison."
GAME_CANCELLED = (
    "<blockquote>🛑 <b>Poison Candy Cancelled</b></blockquote>\n\n"
    "The candies vanish into the dark~ ♡"
)


def lobby_text(host_name, players_text, count, max_players):
    return (
        "<blockquote>🍬 <b>Poison Candy Lobby</b></blockquote>\n\n"
        f"👑 Host: <b>{host_name}</b>\n"
        f"👥 Players: <b>{count}/{max_players}</b>\n\n"
        f"{players_text}\n\n"
        "Tap <b>Join Game</b> to enter.\n"
        "When ready, host can begin.\n\n"
        "<i>❝ Pick sweetly. Die beautifully~ ♡ ❞</i>"
    )


def poison_phase_text(game, waiting):
    return (
        "<blockquote>🔐 <b>Poison Setup</b></blockquote>\n\n"
        "Each player must open DM and secretly choose one poisoned candy.\n\n"
        f"✅ Poison Set: <b>{len(game['poisons'])}/{len(game['players'])}</b>\n"
        f"⏳ Waiting: <b>{waiting}</b>\n\n"
        "<i>❝ Every sweet has a shadow, darling~ ♡ ❞</i>"
    )


def battle_text(game, board, current_name):
    return (
        "<blockquote>🍬 <b>Candy Poison Game</b></blockquote>\n\n"
        f"🎯 <b>{current_name}</b> — Pick a candy!\n"
        "💀 BEWARE!!! Some candies bite back!\n\n"
        f"<pre>{board}</pre>"
    )


def safe_pick_text(player_name, candy):
    return (
        f"✅ {candy} <b>{player_name}</b> picked a safe candy.\n"
        "Mmm, tasty and safe~ ♡"
    )


def poison_pick_text(player_name, poison_owner_name):
    return (
        f"💀 RIP <b>{player_name}</b> — ate "
        f"<b>{poison_owner_name}</b>'s deadly poison!"
    )


def winner_text(winner_name, board):
    return (
        "<blockquote>🏆 <b>Poison Candy Winner</b></blockquote>\n\n"
        f"👑 <b>{winner_name}</b> survived the candy curse!\n\n"
        f"<pre>{board}</pre>\n\n"
        "🪙 Coins and XP have been added~ ♡"
    )


def dm_poison_text(group_name, size):
    return (
        "<blockquote>🍬 <b>Choose Your Poison</b></blockquote>\n\n"
        f"Group: <b>{group_name}</b>\n"
        f"Grid: <b>{size}x{size}</b>\n\n"
        "Pick one candy below.\n"
        "If someone eats it, they are eliminated.\n\n"
        "<i>❝ Hide your poison well~ ♡ ❞</i>"
    )


def poison_set_dm():
    return (
        "🔐 Poison set successfully.\n\n"
        "Return to the group and wait for the candy bloodbath~ ♡"
    )