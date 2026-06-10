# ==========================================================
#  Yumeko Games Bot — Chain Reaction Strings
#  Copyright (c) 2026 Jass
# ==========================================================

ALREADY_RUNNING = "⚛ A Chain Reaction game is already running in this group."
NO_GAME = "❌ No Chain Reaction game is active."
ALREADY_JOINED = "✅ You're already inside the reaction chamber."
GAME_FULL = "⚡ The reaction chamber is full."
HOST_ONLY = "👑 Only the host can do that."
NOT_ENOUGH = "❌ Need at least 2 players."
NOT_PLAYER = "🚫 You're not part of this game."
NOT_YOUR_TURN = "⌛ Not your turn, darling~"
ALREADY_DEAD = "💀 You're already eliminated."
ENEMY_CELL = "🚫 You can only place orbs on empty cells or your own cells."
GAME_CANCELLED = (
    "<blockquote>🛑 <b>Chain Reaction Cancelled</b></blockquote>\n\n"
    "The unstable orbs fade into silence~ ♡"
)


def lobby_text(host_name, players_text, count, max_players):
    return (
        "<blockquote>⚛ <b>CHAIN REACTION</b></blockquote>\n\n"
        "<i>❝ One orb becomes two.\n"
        "Two become chaos.\n"
        "And chaos always chooses a favorite. ♡ ❞</i>\n\n"
        f"🎭 <b>Host:</b> {host_name}\n\n"
        "⚛ Place orbs on the grid.\n"
        "💥 Overloaded cells explode.\n"
        "🌪 Explosions capture nearby cells.\n"
        "🏆 Last player with orbs wins.\n\n"
        "<blockquote>\n"
        "🧪 <b>Reaction Rules</b>\n\n"
        "Corners explode at 2 orbs.\n"
        "Edges explode at 3 orbs.\n"
        "Center cells explode at 4 orbs.\n"
        "</blockquote>\n\n"
        f"👥 <b>Players ({count}/{max_players})</b>\n\n"
        f"{players_text}\n\n"
        "⏳ <i>The reaction chamber is stabilizing...</i>\n\n"
        "♡ Yumeko is waiting for the first explosion."
    )


def arena_text(board, current_name, current_orb, round_no, alive_count):
    return (
        "<blockquote>⚛ <b>CHAIN REACTION</b></blockquote>\n\n"
        f"🎯 Turn: {current_orb} <b>{current_name}</b>\n"
        f"🔢 Round: <b>{round_no}</b>\n"
        f"🟢 Alive: <b>{alive_count}</b>\n\n"
        f"<pre>{board}</pre>\n\n"
        "<i>Choose a cell below. Empty cells or your own cells only~</i>"
    )


def move_text(player_name, orb, row, col, explosions, eliminated_names):
    text = (
        f"{orb} <b>{player_name}</b> placed an orb at "
        f"<b>R{row + 1} C{col + 1}</b>.\n\n"
    )

    if explosions:
        text += (
            "<blockquote>💥 <b>Chain Reaction!</b></blockquote>\n\n"
            f"Explosions triggered: <b>{explosions}</b>\n\n"
        )
    else:
        text += "The chamber trembles quietly...\n\n"

    if eliminated_names:
        text += (
            "💀 <b>Eliminated:</b> "
            + ", ".join(f"<b>{name}</b>" for name in eliminated_names)
            + "\n\n"
        )

    return text


def winner_text(winner_name, winner_orb, scoreboard, coins, xp):
    return (
        "<blockquote>🏆 <b>CHAIN REACTION CHAMPION</b></blockquote>\n\n"
        f"👑 Winner: {winner_orb} <b>{winner_name}</b>\n\n"
        f"🪙 +<b>{coins}</b> Coins\n"
        f"⭐ +<b>{xp}</b> XP\n\n"
        "<blockquote>📊 <b>Final Scoreboard</b></blockquote>\n\n"
        f"{scoreboard}\n\n"
        "<i>❝ Beautiful. One reaction swallowed the whole table~ ♡ ❞</i>"
    )


def no_winner_text():
    return (
        "<blockquote>💀 <b>No Winner</b></blockquote>\n\n"
        "The reaction chamber collapsed before anyone could claim it."
    )


def rules_text():
    return (
        "<blockquote>📖 <b>Chain Reaction Rules</b></blockquote>\n\n"
        "• Players take turns placing orbs.\n"
        "• You can place on empty cells or your own cells.\n"
        "• Corners explode at 2 orbs.\n"
        "• Edges explode at 3 orbs.\n"
        "• Middle cells explode at 4 orbs.\n"
        "• Explosions spread to nearby cells and convert them to your color.\n"
        "• A player is eliminated when they have no orbs after everyone has played once.\n"
        "• Last player with orbs wins.\n\n"
        "🏆 Rewards:\n"
        "🪙 Winner Coins\n"
        "⭐ Winner XP\n"
    )