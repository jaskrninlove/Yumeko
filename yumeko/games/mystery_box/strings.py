# ==========================================================
#  Yumeko Games Bot — Mystery Box Royale Strings
#  Copyright (c) 2026 Jass
# ==========================================================

ALREADY_RUNNING = "🎁 A Mystery Box Royale game is already running in this group."
NO_GAME = "❌ No Mystery Box game is running."
ALREADY_JOINED = "✅ You're already inside the box arena."
GAME_FULL = "⚡ This box arena is full."
HOST_ONLY = "👑 Only the host can do that."
NOT_ENOUGH = "❌ Need at least 2 players to begin."
NOT_PLAYER = "🚫 You're not part of this game."
NOT_YOUR_TURN = "⌛ Not your turn, darling~"
BOX_OPENED = "🎁 This box was already opened."
GAME_CANCELLED = (
    "<blockquote>🛑 <b>Mystery Box Cancelled</b></blockquote>\n\n"
    "The boxes disappear into Yumeko's shadows~ ♡"
)


def lobby_text(host_name, players_text, count, max_players):
    return (
        "<blockquote>🎁 <b>Mystery Box Royale</b></blockquote>\n\n"
        f"👑 Host: <b>{host_name}</b>\n"
        f"👥 Players: <b>{count}/{max_players}</b>\n\n"
        f"{players_text}\n\n"
        "Tap <b>Join Game</b> to enter.\n"
        "Host can begin when enough players join.\n\n"
        "<i>❝ Every box hides a blessing... or a disaster. ♡ ❞</i>"
    )


def arena_text(board, current_name, round_no):
    return (
        "<blockquote>🎁 <b>Mystery Box Arena</b></blockquote>\n\n"
        f"🎯 Turn: <b>{current_name}</b>\n"
        f"🔢 Round: <b>{round_no}</b>\n\n"
        f"<pre>{board}</pre>\n\n"
        "<i>Choose one box below, darling~</i>"
    )


def reward_text(player_name, reward, summary):
    reward_type = reward["type"]
    emoji = reward["emoji"]
    name = reward["name"]

    flavor = {
        "coins": "Yumeko drops coins into your pocket~",
        "xp": "A strange spark of experience enters you~",
        "shield": "Protection wraps around your fate~",
        "bonus_turn": "The table favors you again~",
        "steal": "A sharp little grin appears~",
        "curse": "A cold whisper steals your luck~",
        "bomb": "The box trembles violently~",
        "death": "The box opens its mouth...",
        "crown": "Royalty looks good on you~",
        "jackpot": "Ahahaha~ the arena goes wild!",
        "steal_empty": "No one had enough coins, so Yumeko gave you pity coins~",
    }.get(reward_type, "The box reveals its secret~")

    return (
        f"{emoji} <b>{name}</b>\n\n"
        f"<b>{player_name}</b>\n"
        f"{flavor}\n\n"
        f"{summary}"
    )


def shield_saved_text(player_name, reward_name, summary):
    return (
        "<blockquote>🛡 <b>Shield Activated</b></blockquote>\n\n"
        f"<b>{player_name}</b> opened <b>{reward_name}</b>, "
        "but their shield shattered and saved them.\n\n"
        f"{summary}"
    )


def eliminated_text(player_name, reward_name):
    return (
        "<blockquote>💀 <b>Eliminated</b></blockquote>\n\n"
        f"<b>{player_name}</b> opened <b>{reward_name}</b> and vanished from the arena~"
    )


def steal_choose_text(thief_name, amount):
    return (
        "<blockquote>⚔️ <b>Coin Steal</b></blockquote>\n\n"
        f"<b>{thief_name}</b> can steal up to <b>{amount}</b> coins.\n"
        "Choose a victim below."
    )


def steal_result_text(thief_name, target_name, amount):
    return (
        "<blockquote>⚔️ <b>Coins Stolen</b></blockquote>\n\n"
        f"<b>{thief_name}</b> stole <b>{amount}</b> coins from <b>{target_name}</b>.\n\n"
        "<i>❝ Sweet betrayal, darling~ ♡ ❞</i>"
    )


def winner_text(winner_name, board, scoreboard):
    return (
        "<blockquote>🏆 <b>Mystery Box Champion</b></blockquote>\n\n"
        f"👑 Winner: <b>{winner_name}</b>\n\n"
        f"<pre>{board}</pre>\n\n"
        "<blockquote>📊 <b>Final Scoreboard</b></blockquote>\n\n"
        f"{scoreboard}\n\n"
        "Coins and XP have been added~ ♡"
    )


def rules_text():
    return (
        "<blockquote>🎁 <b>Mystery Box Rules</b></blockquote>\n\n"
        "• Join the lobby.\n"
        "• Host starts the game.\n"
        "• Players open boxes one by one.\n"
        "• Boxes may contain coins, XP, shields, crowns, jackpots, curses, bombs, or death.\n"
        "• Shield saves you from bomb/death once.\n"
        "• Coin Steal lets you steal from another alive player.\n"
        "• Last survivor wins.\n"
        "• If boxes finish first, richest player wins.\n\n"
        "<b>Rewards:</b>\n"
        "🏆 Winner gets bonus coins + XP.\n"
        "💰 Box rewards are also added after the game.\n"
    )