# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
# ==========================================================

from yumeko.games.dart.game import (
    BULLSEYE_COINS,
    BULLSEYE_XP,
    HIT_COINS,
    HIT_XP,
    LOSE_XP,
)


def dart_text(name: str, value: int, result: str):
    if result == "bullseye":
        return (
            f"<blockquote>🎯 <b>BULLSEYE!</b></blockquote>\n\n"
            f"<i>❝ Ahahaha~ straight into the heart of fate. ♡ ❞</i>\n\n"
            f"👤 Player: <b>{name}</b>\n"
            f"🎯 Score: <code>{value}</code>\n\n"
            f"💰 +<b>{BULLSEYE_COINS}</b> coins\n"
            f"✨ +<b>{BULLSEYE_XP}</b> XP"
        )

    if result == "hit":
        return (
            f"<blockquote>🎯 <b>Clean Hit</b></blockquote>\n\n"
            f"<i>❝ Not perfect... but still sharp, darling. ❞</i>\n\n"
            f"👤 Player: <b>{name}</b>\n"
            f"🎯 Score: <code>{value}</code>\n\n"
            f"💰 +<b>{HIT_COINS}</b> coins\n"
            f"✨ +<b>{HIT_XP}</b> XP"
        )

    return (
        f"<blockquote>🎯 <b>Missed Shot</b></blockquote>\n\n"
        f"<i>❝ Oh my~ your aim trembled before fate. ❞</i>\n\n"
        f"👤 Player: <b>{name}</b>\n"
        f"🎯 Score: <code>{value}</code>\n\n"
        f"✨ +<b>{LOSE_XP}</b> XP for daring to throw."
    )