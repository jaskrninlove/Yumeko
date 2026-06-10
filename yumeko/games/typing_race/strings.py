# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
#
#  Developer  : Jass
#  Project    : Yumeko Games Bot
#  Version    : 1.0.0
# ==========================================================

import random

from yumeko.games.typing_race.game import (
    WINNER_COINS,
    WINNER_XP,
    MIN_PLAYERS,
    format_players,
)


def lobby_text(game: dict):
    lines = [
        "Oh my~ another race begins. My heart is already typing faster than yours. ♡",
        "How delightful~ fingers, fear, and fate on one little keyboard.",
        "Ahahaha~ let us see who can survive my sentence.",
    ]

    return (
        f"<blockquote>⌨️ <b>TYPING RACE</b></blockquote>\n\n"
        f"<i>❝ {random.choice(lines)} ❞</i>\n\n"
        f"🎴 Host: <b>{game['host_name']}</b>\n\n"
        f"<b>Rules:</b>\n"
        f"  ◈ Join the race\n"
        f"  ◈ Wait for Yumeko's sentence\n"
        f"  ◈ Type it <b>exactly</b> as shown\n"
        f"  ◈ First correct message wins\n\n"
        f"💰 Winner: <b>{WINNER_COINS}</b> coins\n"
        f"✨ XP: <b>{WINNER_XP}</b>\n\n"
        f"👥 <b>Players ({len(game['players'])}):</b>\n"
        f"{format_players(game['players'])}"
    )


def started_text(sentence: str):
    return (
        f"<blockquote>🚀 <b>Typing Race Started!</b></blockquote>\n\n"
        f"<i>❝ Type carefully, darling. One mistake and fate laughs. ❞</i>\n\n"
        f"Type this sentence exactly:\n\n"
        f"<code>{sentence}</code>\n\n"
        f"<b>First correct message wins.</b>"
    )


def winner_text(name: str, sentence: str):
    return (
        f"<blockquote>🏆 <b>Typing Race Winner!</b></blockquote>\n\n"
        f"<i>❝ Magnificent~ your fingers danced with fate. ♡ ❞</i>\n\n"
        f"⌨️ Champion: <b>{name}</b>\n\n"
        f"Sentence:\n<code>{sentence}</code>\n\n"
        f"💰 +<b>{WINNER_COINS}</b> coins\n"
        f"✨ +<b>{WINNER_XP}</b> XP"
    )


def not_enough_text():
    return (
        f"<blockquote>😔 <b>Not Enough Players</b></blockquote>\n\n"
        f"<i>❝ A race with no rivals? How boring~ ❞</i>\n\n"
        f"At least <b>{MIN_PLAYERS}</b> players are required."
    )


def cancelled_text():
    return (
        f"<blockquote>❌ <b>Typing Race Cancelled</b></blockquote>\n\n"
        f"<i>❝ How unfortunate~ the host lost their nerve. ❞</i>"
    )