# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
#
#  Developer  : Jass
#  Project    : Yumeko Games Bot
#  Version    : 1.0.0
# ==========================================================

from datetime import datetime, timedelta

from yumeko.core.database import db


marriages_col = db["marriages"]
daily_couples_col = db["daily_couples"]


async def get_marriage(chat_id: int, user_id: int):
    return await marriages_col.find_one(
        {"chat_id": chat_id, "users": user_id, "status": "married"}
    )


async def get_any_marriage(user_id: int):
    return await marriages_col.find_one(
        {"users": user_id, "status": "married"},
        sort=[("married_at", -1)],
    )


async def get_profile_marriage(user_id: int, chat_id: int | None = None):
    if chat_id:
        marriage = await get_marriage(chat_id, user_id)
        if marriage:
            return marriage

    return await get_any_marriage(user_id)


async def is_married(chat_id: int, user_id: int):
    return await get_marriage(chat_id, user_id) is not None


async def is_married_anywhere(user_id: int):
    return await get_any_marriage(user_id) is not None


async def create_marriage(chat_id: int, user1: dict, user2: dict):
    doc = {
        "chat_id": chat_id,
        "users": [user1["id"], user2["id"]],
        "user1": user1,
        "user2": user2,
        "status": "married",
        "love_points": 0,
        "last_love_claim": None,
        "married_at": datetime.utcnow(),
    }
    await marriages_col.insert_one(doc)
    return doc


async def divorce_marriage(chat_id: int, user_id: int):
    marriage = await get_marriage(chat_id, user_id)
    if not marriage:
        return None

    await marriages_col.update_one(
        {"_id": marriage["_id"]},
        {"$set": {"status": "divorced", "divorced_at": datetime.utcnow()}},
    )
    return marriage


async def can_claim_love(chat_id: int, user_id: int):
    marriage = await get_marriage(chat_id, user_id)

    if not marriage:
        return False, None, None

    last_claim = marriage.get("last_love_claim")

    if not last_claim:
        return True, marriage, None

    next_claim = last_claim + timedelta(hours=24)

    if datetime.utcnow() >= next_claim:
        return True, marriage, None

    remaining = next_claim - datetime.utcnow()
    hours, rem = divmod(int(remaining.total_seconds()), 3600)
    minutes, _ = divmod(rem, 60)

    return False, marriage, f"{hours}h {minutes}m"


async def claim_love(chat_id: int, user_id: int, points: int):
    marriage = await get_marriage(chat_id, user_id)

    if not marriage:
        return None

    now = datetime.utcnow()

    await marriages_col.update_one(
        {"_id": marriage["_id"]},
        {
            "$inc": {"love_points": points},
            "$set": {"last_love_claim": now},
        },
    )

    marriage["love_points"] = marriage.get("love_points", 0) + points
    marriage["last_love_claim"] = now

    return marriage


async def get_couple_rank(chat_id: int, love_points: int):
    higher = await marriages_col.count_documents(
        {
            "chat_id": chat_id,
            "status": "married",
            "love_points": {"$gt": love_points},
        }
    )
    return higher + 1


async def top_couples(chat_id: int, limit: int = 10):
    cursor = (
        marriages_col.find({"chat_id": chat_id, "status": "married"})
        .sort("love_points", -1)
        .limit(limit)
    )
    return await cursor.to_list(length=limit)


async def get_daily_couple(chat_id: int):
    doc = await daily_couples_col.find_one({"chat_id": chat_id})

    if not doc:
        return None

    expires_at = doc.get("expires_at")

    if expires_at and datetime.utcnow() >= expires_at:
        await daily_couples_col.delete_one({"_id": doc["_id"]})
        return None

    return doc


async def set_daily_couple(chat_id: int, user1: dict, user2: dict):
    expires_at = datetime.utcnow() + timedelta(hours=24)

    doc = {
        "chat_id": chat_id,
        "user1": user1,
        "user2": user2,
        "created_at": datetime.utcnow(),
        "expires_at": expires_at,
    }

    await daily_couples_col.update_one(
        {"chat_id": chat_id},
        {"$set": doc},
        upsert=True,
    )

    return doc


def days_together(married_at):
    if not married_at:
        return 0
    return max((datetime.utcnow() - married_at).days, 0)


def remaining_time(expires_at):
    if not expires_at:
        return "Unknown"

    remaining = expires_at - datetime.utcnow()

    if remaining.total_seconds() <= 0:
        return "Expired"

    hours, rem = divmod(int(remaining.total_seconds()), 3600)
    minutes, _ = divmod(rem, 60)

    return f"{hours}h {minutes}m"