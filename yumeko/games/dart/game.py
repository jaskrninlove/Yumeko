# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
# ==========================================================

from yumeko.database.users import add_xp, add_coins

BULLSEYE_COINS = 60
BULLSEYE_XP = 30
HIT_COINS = 20
HIT_XP = 10
LOSE_XP = 4


async def reward_dart(user_id: int, value: int):
    if value == 6:
        await add_coins(user_id, BULLSEYE_COINS)
        await add_xp(user_id, BULLSEYE_XP)
        return "bullseye"

    if value >= 4:
        await add_coins(user_id, HIT_COINS)
        await add_xp(user_id, HIT_XP)
        return "hit"

    await add_xp(user_id, LOSE_XP)
    return "miss"