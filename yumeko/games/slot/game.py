# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
#
#  Developer  : Jass
#  Project    : Yumeko Games Bot
#  Version    : 1.0.0
# ==========================================================

from yumeko.database.users import add_xp, add_coins

JACKPOT_COINS = 100
JACKPOT_XP = 50

WIN_COINS = 30
WIN_XP = 15

LOSE_XP = 4


async def reward_slot(user_id: int, value: int):
    # Telegram slot jackpot value is usually 64
    if value == 64:
        await add_coins(user_id, JACKPOT_COINS)
        await add_xp(user_id, JACKPOT_XP)
        return "jackpot"

    # Some decent reward for high rolls
    if value >= 50:
        await add_coins(user_id, WIN_COINS)
        await add_xp(user_id, WIN_XP)
        return "win"

    await add_xp(user_id, LOSE_XP)
    return "lose"