# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
#
#  Developer  : Jass
#  Project    : Yumeko Games Bot
#  Version    : 1.0.0
# ==========================================================

from yumeko.database.users import add_xp, add_coins

MIN_DICE = 1
MAX_DICE = 6

WIN_COINS = 25
WIN_XP = 12
LOSE_XP = 4
PLAY_XP = 2


def normalize_guess(text: str):
    if not text:
        return None

    try:
        number = int(text)
    except ValueError:
        return None

    if MIN_DICE <= number <= MAX_DICE:
        return number

    return None


async def reward_dice(user_id: int, guessed: bool, won: bool):
    if not guessed:
        await add_xp(user_id, PLAY_XP)
        return

    if won:
        await add_coins(user_id, WIN_COINS)
        await add_xp(user_id, WIN_XP)
    else:
        await add_xp(user_id, LOSE_XP)