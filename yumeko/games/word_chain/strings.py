# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
# ==========================================================

import random

from yumeko.games.word_chain.game import (
    JOIN_TIME,
    MIN_PLAYERS,
    MAX_PLAYERS,
    WORDS_PER_TURN,
    PLAYER_LIVES,
    LOSER_XP,
    WINNER_COINS,
    WINNER_XP,
    format_players,
    format_alive,
    format_scores,
    get_turn_time,
)


def mention_player(player: dict):
    return f'<a href="tg://user?id={player["id"]}">{player["name"]}</a>'


def get_next_player(game: dict):
    if not game or not game.get("alive"):
        return None

    if not game["alive"]:
        return None

    index = game.get("current_player_index", 0)

    if index >= len(game["alive"]):
        index = 0

    user_id = game["alive"][index]
    return game["players"].get(user_id)


def lobby_text(game: dict):
    return (
        "<blockquote>🔤 <b>WORD CHAIN — SURVIVAL TABLE</b></blockquote>\n\n"
        f"<i>❝ {random.choice(['Words are cards, darling. Play the right one.', 'Let us see whose mind survives the table.', 'A little vocabulary. A little pressure. A little madness.'])} ♡ ❞</i>\n\n"
        f"🎴 <b>Host:</b> {game['host_name']}\n\n"
        "<blockquote>🎮 <b>How To Join</b></blockquote>\n"
        "Send <code>/join</code> or tap the join button below.\n\n"
        "<blockquote>📜 <b>Rules</b></blockquote>\n"
        f"◈ Players: <b>{MIN_PLAYERS}-{MAX_PLAYERS}</b>\n"
        f"◈ Words per turn: <b>{WORDS_PER_TURN}</b>\n"
        f"◈ Lives each player: ❤️ <b>{PLAYER_LIVES}</b>\n"
        "◈ Word must start with the required letter\n"
        "◈ Word must exist in Yumeko's dictionary\n"
        "◈ Repeated words are not allowed\n"
        "◈ Difficulty slowly rises: <b>3 → 5 → 8 → 10 → 11 → 12</b>\n"
        "◈ Timer starts at <b>30s</b> and slowly drops to <b>15s</b>\n\n"
        f"⏳ Lobby closes in <b>{JOIN_TIME}s</b>\n\n"
        f"👥 <b>Joined Players ({len(game['players'])})</b>\n"
        f"{format_players(game)}"
    )


def join_countdown_text(seconds_left: int):
    return (
        "<blockquote>🔤 <b>Word Chain Lobby</b></blockquote>\n\n"
        f"<i>❝ {seconds_left} seconds left, darling. Join before fate closes the door. ♡ ❞</i>\n\n"
        "Send <code>/join</code> to enter."
    )


def joined_text(name: str, count: int):
    return (
        "<blockquote>🎭 <b>Player Joined</b></blockquote>\n\n"
        f"<b>{name}</b> joined Word Chain.\n\n"
        f"👥 Players now: <b>{count}</b>"
    )


def not_enough_text(game: dict):
    return (
        "<blockquote>😔 <b>Word Chain Cancelled</b></blockquote>\n\n"
        f"<i>❝ Only {len(game['players'])} player joined. How lonely~ ♡ ❞</i>\n\n"
        f"At least <b>{MIN_PLAYERS}</b> players are required."
    )


def turn_text(game: dict, player: dict):
    seconds = get_turn_time(game)
    current = mention_player(player)

    return (
        "<blockquote>🎯 <b>YOUR TURN — WORD CHAIN</b></blockquote>\n\n"
        f"🎲 <b>Current Player:</b> {current}\n"
        f"🔤 <b>Start With:</b> <code>{game['current_letter'].upper()}</code>\n"
        f"📏 <b>Minimum Length:</b> <code>{game['required_length']}</code>\n"
        f"⏳ <b>Time:</b> <code>{seconds}s</code>\n\n"
        "<i>❝ Your word is your bet. Don't waste it, darling. ♡ ❞</i>\n\n"
        "<blockquote>👥 <b>Survivors</b></blockquote>\n"
        f"{format_alive(game)}"
    )


def valid_word_text(game: dict, player: dict, result: dict, name: str):
    seconds = get_turn_time(game)
    next_player = mention_player(player) if player else "Unknown"
    word = result.get("word", "")
    xp = result.get("xp", 0)
    coins = result.get("coins", 0)
    length = result.get("length", len(word))

    return (
        "<blockquote>✅ <b>WORD ACCEPTED</b></blockquote>\n\n"
        f"<i>❝ <b>{name}</b> survived with <code>{word}</code>. Lovely~ ♡ ❞</i>\n\n"
        f"🔤 <b>Accepted Word:</b> <code>{word.upper()}</code>\n"
        f"📏 <b>Word Length:</b> <code>{length}</code>\n"
        f"✨ <b>XP Earned:</b> +<code>{xp}</code>\n"
        f"💰 <b>Coins Earned:</b> +<code>{coins}</code>\n\n"
        "<blockquote>🎯 <b>Next Turn</b></blockquote>\n"
        f"👤 <b>Next Player:</b> {next_player}\n"
        f"🔤 <b>Start With:</b> <code>{game['current_letter'].upper()}</code>\n"
        f"📏 <b>Minimum Length:</b> <code>{game['required_length']}</code>\n"
        f"⏳ <b>Time:</b> <code>{seconds}s</code>"
    )


def timeout_text(game: dict, player: dict):
    next_player = get_next_player(game)
    next_text = mention_player(next_player) if next_player else "Unknown"

    return (
        "<blockquote>⏳ <b>TIME OUT</b></blockquote>\n\n"
        f"<i>❝ Too slow, <b>{player['name']}</b>. The chain does not wait. ❞</i>\n\n"
        f"💔 <b>{player['name']}</b> lost 1 life.\n"
        f"❤️ Remaining Lives: <code>{player['lives']}</code>\n\n"
        "<blockquote>🎯 <b>Next Turn</b></blockquote>\n"
        f"👤 <b>Next Player:</b> {next_text}\n"
        f"🔤 <b>Start With:</b> <code>{game['current_letter'].upper()}</code>\n"
        f"📏 <b>Minimum Length:</b> <code>{game['required_length']}</code>\n"
        f"⏳ <b>Time:</b> <code>{get_turn_time(game)}s</code>\n\n"
        "<blockquote>👥 <b>Survivors</b></blockquote>\n"
        f"{format_alive(game)}"
    )


def eliminated_text(game: dict, player: dict):
    next_player = get_next_player(game)
    next_text = mention_player(next_player) if next_player else "Unknown"

    return (
        "<blockquote>💀 <b>PLAYER ELIMINATED</b></blockquote>\n\n"
        f"<i>❝ <b>{player['name']}</b> has no lives left. Farewell, darling. ♡ ❞</i>\n\n"
        "<blockquote>🎯 <b>Next Turn</b></blockquote>\n"
        f"👤 <b>Next Player:</b> {next_text}\n"
        f"🔤 <b>Start With:</b> <code>{game['current_letter'].upper()}</code>\n"
        f"📏 <b>Minimum Length:</b> <code>{game['required_length']}</code>\n"
        f"⏳ <b>Time:</b> <code>{get_turn_time(game)}s</code>\n\n"
        "<blockquote>👥 <b>Remaining Survivors</b></blockquote>\n"
        f"{format_alive(game)}"
    )


def winner_text(game: dict, winner: dict):
    champion = mention_player(winner)

    return (
        "<blockquote>🏆 <b>WORD CHAIN WINNER</b></blockquote>\n\n"
        f"<i>❝ Ahahaha~ {champion} survived the chain. Magnificent. ♡ ❞</i>\n\n"
        f"👑 <b>Champion:</b> {champion}\n"
        f"🔤 <b>Words:</b> <code>{winner['words']}</code>\n"
        f"🎯 <b>Score:</b> <code>{winner['score']}</code>\n\n"
        "<blockquote>📊 <b>Final Scores</b></blockquote>\n"
        f"{format_scores(game)}\n\n"
        f"💰 Winner Coins: +<b>{WINNER_COINS}</b>\n"
        f"✨ Winner XP: +<b>{WINNER_XP}</b>\n"
        f"📉 Others: +<b>{LOSER_XP}</b> XP"
    )


def invalid_word_text(reason: str, game: dict):
    if reason == "not_turn":
        return "Not your turn, darling~"

    if reason == "wrong_letter":
        return (
            "<blockquote>❌ <b>Wrong Letter</b></blockquote>\n\n"
            f"This word must start with: <code>{game['current_letter'].upper()}</code>"
        )

    if reason == "too_short":
        return (
            "<blockquote>❌ <b>Too Short</b></blockquote>\n\n"
            f"Minimum word length is: <code>{game['required_length']}</code>"
        )

    if reason == "used":
        return (
            "<blockquote>❌ <b>Word Already Used</b></blockquote>\n\n"
            "This word is already guessed. Play something new, darling."
        )

    if reason == "invalid":
        return (
            "<blockquote>❌ <b>Invalid Word</b></blockquote>\n\n"
            "Only letters are allowed, darling~"
        )

    return (
        "<blockquote>❌ <b>Invalid Word</b></blockquote>\n\n"
        "Yumeko rejected this word."
    )


def stopped_text():
    return (
        "<blockquote>🛑 <b>Word Chain Stopped</b></blockquote>\n\n"
        "<i>❝ The chain breaks here... for now. ♡ ❞</i>"
    )