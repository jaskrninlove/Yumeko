# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
#
#  Developer  : Jass
#  Project    : Yumeko Games Bot
#  Version    : 1.0.0
# ==========================================================

from datetime import datetime, timedelta

from yumeko.core.database import users_col


async def get_user(user_id: int):
    user = await users_col.find_one({"user_id": user_id})

    if not user:
        user = {
            "user_id": user_id,
            "coins": 0,
            "xp": 0,
            "wins": 0,
            "losses": 0,
            "games_played": 0,
        }
        await users_col.insert_one(user)

    return user


async def add_coins(user_id: int, amount: int):
    await get_user(user_id)
    await users_col.update_one(
        {"user_id": user_id},
        {"$inc": {"coins": amount}},
    )


async def remove_coins(user_id: int, amount: int):
    await get_user(user_id)
    await users_col.update_one(
        {"user_id": user_id},
        {"$inc": {"coins": -amount}},
    )


async def add_xp(user_id: int, amount: int):
    await get_user(user_id)
    await users_col.update_one(
        {"user_id": user_id},
        {"$inc": {"xp": amount}},
    )


async def get_balance(user_id: int):
    user = await get_user(user_id)
    return {
        "coins": user.get("coins", 0),
        "xp": user.get("xp", 0),
        "wins": user.get("wins", 0),
        "losses": user.get("losses", 0),
        "games_played": user.get("games_played", 0),
    }


async def can_use_cooldown(user_id: int, key: str, hours: int):
    user = await get_user(user_id)
    last = user.get(key)

    if not last:
        return True, None

    next_time = last + timedelta(hours=hours)

    if datetime.utcnow() >= next_time:
        return True, None

    remaining = next_time - datetime.utcnow()
    h, rem = divmod(int(remaining.total_seconds()), 3600)
    m, _ = divmod(rem, 60)

    return False, f"{h}h {m}m"


async def set_cooldown(user_id: int, key: str):
    await users_col.update_one(
        {"user_id": user_id},
        {"$set": {key: datetime.utcnow()}},
    )