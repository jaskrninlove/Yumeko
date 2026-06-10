# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
#
#  Developer  : Jass
#  Project    : Yumeko Games Bot
#  Version    : 1.0.0
#
#  GitHub     : Private
#  License    : MIT License
#
#  This file is part of Yumeko Games Bot.
#  Unauthorized removal of this notice is discouraged.
#
#  © 2026 Jass. All Rights Reserved.
# ==========================================================

from datetime import datetime, timedelta

from yumeko.core.database import users_col


DAILY_COINS = 100
DAILY_XP = 20
DAILY_COOLDOWN_HOURS = 24


async def claim_daily(user_id: int):
    user = await users_col.find_one({"user_id": user_id})

    now = datetime.utcnow()

    if not user:
        return {
            "success": False,
            "reason": "user_not_found",
        }

    last_daily = user.get("last_daily")

    if last_daily:
        next_claim = last_daily + timedelta(hours=DAILY_COOLDOWN_HOURS)

        if now < next_claim:
            remaining = next_claim - now

            hours, remainder = divmod(int(remaining.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)

            return {
                "success": False,
                "reason": "cooldown",
                "hours": hours,
                "minutes": minutes,
                "seconds": seconds,
            }

    await users_col.update_one(
        {"user_id": user_id},
        {
            "$inc": {
                "coins": DAILY_COINS,
                "xp": DAILY_XP,
            },
            "$set": {
                "last_daily": now,
            },
        },
    )

    return {
        "success": True,
        "coins": DAILY_COINS,
        "xp": DAILY_XP,
    }