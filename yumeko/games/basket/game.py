# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
# ==========================================================

from yumeko.database.users import add_xp, add_coins

PERFECT_COINS = 50
PERFECT_XP = 25
SCORE_COINS = 20
SCORE_XP = 10
MISS_XP = 4


async def reward_basket(user_id: int, value: int):
    # Telegram basketball: 4 or 5 usually means scored, 5 is best
    if value == 5:
        await add_coins(user_id, PERFECT_COINS)
        await add_xp(user_id, PERFECT_XP)
        return "perfect"

    if value >= 4:
        await add_coins(user_id, SCORE_COINS)
        await add_xp(user_id, SCORE_XP)
        return "score"

    await add_xp(user_id, MISS_XP)
    return "miss"