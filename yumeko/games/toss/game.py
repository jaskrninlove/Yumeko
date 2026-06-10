# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
#
#  Developer  : Jass
#  Project    : Yumeko Games Bot
#  Version    : 1.0.0
# ==========================================================

import random

from yumeko.database.users import add_xp, add_coins


RESULTS = ["heads", "tails"]

WIN_COINS = 20
WIN_XP = 10
LOSE_XP = 3
PLAY_XP = 2


def flip_coin():
    return random.choice(RESULTS)


def normalize_guess(text: str):
    if not text:
        return None

    guess = text.lower().strip()

    if guess in ["h", "head", "heads"]:
        return "heads"

    if guess in ["t", "tail", "tails"]:
        return "tails"

    return None


async def reward_toss(user_id: int, guessed: bool, won: bool):
    if not guessed:
        await add_xp(user_id, PLAY_XP)
        return

    if won:
        await add_coins(user_id, WIN_COINS)
        await add_xp(user_id, WIN_XP)
    else:
        await add_xp(user_id, LOSE_XP)