# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
# ==========================================================

import random

from yumeko.games.bomb_party.game import (
    JOIN_TIME,
    TURN_TIME,
    MIN_PLAYERS,
    MAX_PLAYERS,
    PLAYER_LIVES,
    VALID_WORD_XP,
    LOSER_XP,
    WINNER_COINS,
    WINNER_XP,
    format_players,
    format_alive,
    format_scores,
)


def lobby_text(game: dict):
    return (
        f"<blockquote>💣 <b>BOMB PARTY — SURVIVAL</b></blockquote>\n\n"
        f"<i>❝ {random.choice(['Oh my~ a bomb on the table. How thrilling. ♡', 'Every word could save you... or ruin you.', 'The timer is hungry. Feed it a word before it explodes.'])} ❞</i>\n\n"
        f"🎴 Host: <b>{game['host_name']}</b>\n\n"
        f"<b>How to join:</b>\n"
        f"Send <code>/join</code> or tap the button below.\n\n"
        f"<b>Rules:</b>\n"
        f"  ◈ {MIN_PLAYERS}–{MAX_PLAYERS} players\n"
        f"  ◈ Yumeko gives letters like <code>ca</code>\n"
        f"  ◈ Your word must contain those letters\n"
        f"  ◈ You have <b>{TURN_TIME}s</b> per turn\n"
        f"  ◈ Timeout = lose 1 life\n"
        f"  ◈ Each player has <b>{PLAYER_LIVES}</b> lives\n"
        f"  ◈ Difficulty increases slowly\n"
        f"  ◈ Last survivor wins\n\n"
        f"⏳ Lobby closes in <b>{JOIN_TIME}s</b>\n\n"
        f"👥 <b>Players ({len(game['players'])}):</b>\n"
        f"{format_players(game)}"
    )


def join_countdown_text(seconds_left: int):
    return (
        f"<blockquote>💣 <b>Bomb Party Lobby</b></blockquote>\n\n"
        f"<i>❝ {seconds_left} seconds left. Join before the fuse burns out. ❞</i>\n\n"
        f"Send <code>/join</code> to enter."
    )


def joined_text(name: str, count: int):
    return f"💣 <b>{name}</b> joined Bomb Party.\n\nPlayers now: <b>{count}</b>"


def not_enough_text(game: dict):
    return (
        f"<blockquote>😔 <b>Bomb Party Cancelled</b></blockquote>\n\n"
        f"<i>❝ Only {len(game['players'])} player joined. A bomb with no victims? How boring~ ❞</i>\n\n"
        f"At least <b>{MIN_PLAYERS}</b> players are required."
    )


def turn_text(game: dict, player: dict):
    return (
        f"<blockquote>💣 <b>Bomb Party Turn</b></blockquote>\n\n"
        f"<i>❝ The fuse is burning. Speak fast, darling. ❞</i>\n\n"
        f"🎯 Current Player: <b>{player['name']}</b>\n"
        f"🔤 Word must contain: <code>{game['current_syllable']}</code>\n"
        f"⏳ Time: <b>{TURN_TIME}s</b>\n"
        f"🎲 Round: <code>{game['round']}</code>\n\n"
        f"👥 <b>Survivors:</b>\n{format_alive(game)}"
    )


def valid_word_text(game: dict, player: dict, word: str, name: str):
    return (
        f"<blockquote>✅ <b>Word Accepted</b></blockquote>\n\n"
        f"<i>❝ <b>{name}</b> survived with <code>{word}</code>. Delicious. ♡ ❞</i>\n\n"
        f"✨ +<b>{VALID_WORD_XP}</b> XP\n\n"
        f"🎯 Current Player: <b>{player['name']}</b>\n\n"
        f"🔤 Word must contain: <code>{game['current_syllable']}</code>\n\n"
        f"⏳ Time: <b>{TURN_TIME}s</b>\n"
        f"🎲 Round: <code>{game['round']}</code>"
    )


def timeout_text(game: dict, player: dict):
    return (
        f"<blockquote>⏳ <b>Time Out</b></blockquote>\n\n"
        f"<i>❝ Too slow, <b>{player['name']}</b>. The bomb takes a life. ❞</i>\n\n"
        f"<b>{player['name']}</b> lost 1 life.\n"
        f"Remaining lives: ❤️ <code>{player['lives']}</code>\n\n"
        f"👥 <b>Survivors:</b>\n{format_alive(game)}"
    )


def eliminated_text(game: dict, player: dict):
    return (
        f"<blockquote>💥 <b>BOOM!</b></blockquote>\n\n"
        f"<i>❝ <b>{player['name']}</b> has no lives left. The bomb has chosen. ❞</i>\n\n"
        f"👥 <b>Remaining:</b>\n{format_alive(game)}"
    )


def winner_text(game: dict, winner: dict):
    return (
        f"<blockquote>🏆 <b>BOMB PARTY WINNER</b></blockquote>\n\n"
        f"<i>❝ Ahahaha~ <b>{winner['name']}</b> survived the explosion. Magnificent. ♡ ❞</i>\n\n"
        f"👑 Champion: <b>{winner['name']}</b>\n"
        f"💣 Words: <code>{winner['words']}</code>\n"
        f"🎯 Score: <code>{winner['score']}</code>\n\n"
        f"📊 <b>Final Scores:</b>\n{format_scores(game)}\n\n"
        f"💰 +<b>{WINNER_COINS}</b> coins\n"
        f"✨ +<b>{WINNER_XP}</b> XP\n"
        f"📉 Others: +<b>{LOSER_XP}</b> XP"
    )


def invalid_word_text(reason: str, game: dict):
    if reason == "not_turn":
        return "Not your turn, darling~"

    if reason == "missing":
        return f"Wrong word. It must contain <code>{game['current_syllable']}</code>."

    if reason == "too_short":
        return "Too short. Use at least <code>3</code> letters."

    if reason == "used":
        return "This word is already used. Try something fresh."

    if reason == "invalid":
        return "Only letters are allowed, darling~"

    return "Invalid word."


def stopped_text():
    return (
        f"<blockquote>🛑 <b>Bomb Party Stopped</b></blockquote>\n\n"
        f"<i>❝ The bomb sleeps... for now. ❞</i>"
    )