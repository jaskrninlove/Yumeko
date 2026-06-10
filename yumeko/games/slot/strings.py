# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
# ==========================================================

from yumeko.games.slot.game import (
    JACKPOT_COINS,
    JACKPOT_XP,
    WIN_COINS,
    WIN_XP,
    LOSE_XP,
)


def slot_text(name: str, value: int, result: str):
    if result == "jackpot":
        return (
            f"<blockquote>🎰 <b>JACKPOT!</b></blockquote>\n\n"
            f"<i>❝ Ahahaha~ the machine screamed your name, darling. ♡ ❞</i>\n\n"
            f"👤 Player: <b>{name}</b>\n"
            f"🎰 Slot Value: <code>{value}</code>\n\n"
            f"💰 +<b>{JACKPOT_COINS}</b> coins\n"
            f"✨ +<b>{JACKPOT_XP}</b> XP"
        )

    if result == "win":
        return (
            f"<blockquote>🎰 <b>Lucky Spin</b></blockquote>\n\n"
            f"<i>❝ Not a jackpot, but fate still smiled a little. ♡ ❞</i>\n\n"
            f"👤 Player: <b>{name}</b>\n"
            f"🎰 Slot Value: <code>{value}</code>\n\n"
            f"💰 +<b>{WIN_COINS}</b> coins\n"
            f"✨ +<b>{WIN_XP}</b> XP"
        )

    return (
        f"<blockquote>🎰 <b>Slot Machine</b></blockquote>\n\n"
        f"<i>❝ Oh my~ the machine devoured your luck this time. ❞</i>\n\n"
        f"👤 Player: <b>{name}</b>\n"
        f"🎰 Slot Value: <code>{value}</code>\n\n"
        f"✨ +<b>{LOSE_XP}</b> XP for daring to spin."
    )