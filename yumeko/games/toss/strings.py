# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
# ==========================================================

from yumeko.games.toss.game import WIN_COINS, WIN_XP, LOSE_XP, PLAY_XP


def toss_text(name: str, result: str, guess: str | None):
    pretty = "Heads" if result == "heads" else "Tails"
    emoji = "🪙"

    if guess is None:
        return (
            f"<blockquote>{emoji} <b>Coin Flip</b></blockquote>\n\n"
            f"<i>❝ Yumeko flips the coin and lets fate whisper~ ❞</i>\n\n"
            f"👤 Player: <b>{name}</b>\n"
            f"🎲 Result: <b>{pretty}</b>\n\n"
            f"✨ +<b>{PLAY_XP}</b> XP for tempting fate."
        )

    guessed = "Heads" if guess == "heads" else "Tails"

    if guess == result:
        return (
            f"<blockquote>{emoji} <b>Correct Guess!</b></blockquote>\n\n"
            f"<i>❝ Ahahaha~ fate smiled at you, darling. ♡ ❞</i>\n\n"
            f"👤 Player: <b>{name}</b>\n"
            f"🎯 Your Guess: <b>{guessed}</b>\n"
            f"🎲 Result: <b>{pretty}</b>\n\n"
            f"💰 +<b>{WIN_COINS}</b> coins\n"
            f"✨ +<b>{WIN_XP}</b> XP"
        )

    return (
        f"<blockquote>{emoji} <b>Wrong Guess</b></blockquote>\n\n"
        f"<i>❝ Oh my~ fate betrayed you this time. Delicious. ❞</i>\n\n"
        f"👤 Player: <b>{name}</b>\n"
        f"🎯 Your Guess: <b>{guessed}</b>\n"
        f"🎲 Result: <b>{pretty}</b>\n\n"
        f"✨ +<b>{LOSE_XP}</b> XP for daring to play."
    )


def usage_text():
    return (
        "<blockquote>🪙 <b>Coin Flip</b></blockquote>\n\n"
        "Use:\n"
        "<code>/toss</code>\n"
        "<code>/toss heads</code>\n"
        "<code>/toss tails</code>"
    )