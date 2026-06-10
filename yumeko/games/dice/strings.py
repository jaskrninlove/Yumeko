# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
# ==========================================================

from yumeko.games.dice.game import WIN_COINS, WIN_XP, LOSE_XP, PLAY_XP


def dice_text(name: str, result: int, guess: int | None):
    if guess is None:
        return (
            f"<blockquote>🎲 <b>Dice Roll</b></blockquote>\n\n"
            f"<i>❝ Yumeko lets the dice fall... fate has spoken. ♡ ❞</i>\n\n"
            f"👤 Player: <b>{name}</b>\n"
            f"🎲 Rolled: <b>{result}</b>\n\n"
            f"✨ +<b>{PLAY_XP}</b> XP for tempting fate."
        )

    if guess == result:
        return (
            f"<blockquote>🏆 <b>Perfect Guess!</b></blockquote>\n\n"
            f"<i>❝ Ahahaha~ you read fate like an open card. Magnificent. ♡ ❞</i>\n\n"
            f"👤 Player: <b>{name}</b>\n"
            f"🎯 Your Guess: <b>{guess}</b>\n"
            f"🎲 Rolled: <b>{result}</b>\n\n"
            f"💰 +<b>{WIN_COINS}</b> coins\n"
            f"✨ +<b>{WIN_XP}</b> XP"
        )

    return (
        f"<blockquote>😈 <b>Wrong Guess</b></blockquote>\n\n"
        f"<i>❝ Fate had other plans for you, darling. ❞</i>\n\n"
        f"👤 Player: <b>{name}</b>\n"
        f"🎯 Your Guess: <b>{guess}</b>\n"
        f"🎲 Rolled: <b>{result}</b>\n\n"
        f"✨ +<b>{LOSE_XP}</b> XP for daring to roll."
    )


def usage_text():
    return (
        "<blockquote>🎲 <b>Dice Roll</b></blockquote>\n\n"
        "Use:\n"
        "<code>/dice</code>\n"
        "<code>/dice 1</code>\n"
        "<code>/dice 2</code>\n"
        "<code>/dice 3</code>\n"
        "<code>/dice 4</code>\n"
        "<code>/dice 5</code>\n"
        "<code>/dice 6</code>"
    )