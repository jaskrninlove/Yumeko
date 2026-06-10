# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
# ==========================================================

from yumeko.games.basket.game import (
    PERFECT_COINS,
    PERFECT_XP,
    SCORE_COINS,
    SCORE_XP,
    MISS_XP,
)


def basket_text(name: str, value: int, result: str):
    if result == "perfect":
        return (
            f"<blockquote>🏀 <b>PERFECT SHOT!</b></blockquote>\n\n"
            f"<i>❝ Ahahaha~ straight through the hoop. Beautiful. ♡ ❞</i>\n\n"
            f"👤 Player: <b>{name}</b>\n"
            f"🏀 Score Value: <code>{value}</code>\n\n"
            f"💰 +<b>{PERFECT_COINS}</b> coins\n"
            f"✨ +<b>{PERFECT_XP}</b> XP"
        )

    if result == "score":
        return (
            f"<blockquote>🏀 <b>Nice Shot</b></blockquote>\n\n"
            f"<i>❝ Not flawless, but the ball obeyed you. ♡ ❞</i>\n\n"
            f"👤 Player: <b>{name}</b>\n"
            f"🏀 Score Value: <code>{value}</code>\n\n"
            f"💰 +<b>{SCORE_COINS}</b> coins\n"
            f"✨ +<b>{SCORE_XP}</b> XP"
        )

    return (
        f"<blockquote>🏀 <b>Missed Shot</b></blockquote>\n\n"
        f"<i>❝ Oh my~ the hoop rejected your wish. Try again, darling. ❞</i>\n\n"
        f"👤 Player: <b>{name}</b>\n"
        f"🏀 Score Value: <code>{value}</code>\n\n"
        f"✨ +<b>{MISS_XP}</b> XP for taking the shot."
    )