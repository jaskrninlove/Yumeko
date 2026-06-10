# ==========================================================
#  Yumeko Games Bot — Battleship Royale Strings
#  Copyright (c) 2026 Jass
# ==========================================================

ALREADY_RUNNING = "🚢 A Battleship Royale match is already running in this group."
NO_GAME = "❌ No Battleship match is active."
ALREADY_JOINED = "✅ You're already commanding a fleet."
GAME_FULL = "⚡ Battleship only supports 2 players."
HOST_ONLY = "👑 Only the host can do that."
NOT_ENOUGH = "❌ Need 2 players to begin."
NOT_PLAYER = "🚫 You're not part of this battle."
NOT_YOUR_TURN = "⌛ Not your turn, captain~"
ALREADY_ATTACKED = "🚫 That coordinate was already attacked."
GAME_CANCELLED = (
    "<blockquote>🛑 <b>Battleship Cancelled</b></blockquote>\n\n"
    "The sea returns to silence~ ♡"
)


def lobby_text(host_name, players_text, count, max_players):
    return (
        "<blockquote>🚢 <b>BATTLESHIP ROYALE</b></blockquote>\n\n"
        "<i>❝ The sea is calm.\n"
        "The cannons are loaded.\n"
        "Only one fleet returns home. ♡ ❞</i>\n\n"
        f"🎭 <b>Host:</b> {host_name}\n\n"
        "🚢 Deploy your hidden fleet.\n"
        "🎯 Fire at enemy waters.\n"
        "💥 Hit their ships.\n"
        "🏆 Sink every vessel to win.\n\n"
        "<blockquote>\n"
        "⚓ <b>Naval Warfare</b>\n\n"
        "Your ships are hidden.\n"
        "Enemy waters are unknown.\n"
        "Hits give an extra turn.\n"
        "</blockquote>\n\n"
        f"👥 <b>Players ({count}/{max_players})</b>\n\n"
        f"{players_text}\n\n"
        "⏳ <i>The fleets are preparing for battle...</i>\n\n"
        "♡ Yumeko watches from the shore."
    )


def arena_text(current_name, enemy_board, own_board):
    return (
        "<blockquote>🚢 <b>BATTLESHIP ROYALE</b></blockquote>\n\n"
        f"🎯 Turn: <b>{current_name}</b>\n\n"
        "<blockquote>🎯 <b>Enemy Waters</b></blockquote>\n"
        f"<pre>{enemy_board}</pre>\n\n"
        "<blockquote>🛡 <b>Your Fleet</b></blockquote>\n"
        f"<pre>{own_board}</pre>\n\n"
        "<i>Choose a coordinate to fire, captain~</i>"
    )


def attack_text(attacker_name, row, col, result_word):
    coord = f"{chr(65 + row)}{col + 1}"

    if result_word == "miss":
        return (
            "<blockquote>⭕ <b>MISS</b></blockquote>\n\n"
            f"<b>{attacker_name}</b> fired at <b>{coord}</b>.\n"
            "Only waves answered back~"
        )

    if result_word == "hit":
        return (
            "<blockquote>💥 <b>HIT!</b></blockquote>\n\n"
            f"<b>{attacker_name}</b> struck <b>{coord}</b>.\n"
            "The enemy hull screams~ ♡\n\n"
            "<i>Hit grants another turn.</i>"
        )

    return (
        "<blockquote>🎯 <b>SHOT FIRED</b></blockquote>\n\n"
        f"<b>{attacker_name}</b> fired at <b>{coord}</b>."
    )


def sunk_text(ship_name):
    return (
        "<blockquote>💀 <b>SHIP SUNK!</b></blockquote>\n\n"
        f"Enemy <b>{ship_name}</b> has disappeared beneath the waves~"
    )


def winner_text(winner_name, scoreboard, coins, xp):
    return (
        "<blockquote>🏆 <b>BATTLESHIP VICTORY</b></blockquote>\n\n"
        f"👑 Admiral: <b>{winner_name}</b>\n\n"
        f"🪙 +<b>{coins}</b> Coins\n"
        f"⭐ +<b>{xp}</b> XP\n\n"
        "<blockquote>📊 <b>Final Fleet Report</b></blockquote>\n\n"
        f"{scoreboard}\n\n"
        "<i>❝ The sea belongs to the bold, darling~ ♡ ❞</i>"
    )


def rules_text():
    return (
        "<blockquote>📖 <b>Battleship Rules</b></blockquote>\n\n"
        "• Battleship is a 2-player naval battle.\n"
        "• Ships are placed automatically and hidden.\n"
        "• Players take turns firing at enemy waters.\n"
        "• ⭕ Miss means turn passes.\n"
        "• 💥 Hit gives another turn.\n"
        "• 💀 Sink all enemy ships to win.\n\n"
        "🏆 Rewards:\n"
        "🪙 Winner Coins\n"
        "⭐ Winner XP\n"
    )