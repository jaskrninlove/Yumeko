# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
# ==========================================================

from datetime import datetime
from yumeko.core.database import db

achievements_col = db["achievements"]


async def ensure_achievement_indexes():
    try:
        await achievements_col.create_index("user_id", unique=True)
    except Exception:
        pass


async def get_user_achievements(user_id: int):
    doc = await achievements_col.find_one({"user_id": user_id})

    if not doc:
        doc = {
            "user_id": user_id,
            "badges": [],
            "unlocked_at": {},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        await achievements_col.insert_one(doc)

    return doc


async def has_badge(user_id: int, badge_id: str):
    doc = await get_user_achievements(user_id)
    return badge_id in doc.get("badges", [])


async def unlock_badge(user_id: int, badge_id: str):
    doc = await get_user_achievements(user_id)

    if badge_id in doc.get("badges", []):
        return False

    await achievements_col.update_one(
        {"user_id": user_id},
        {
            "$addToSet": {"badges": badge_id},
            "$set": {
                f"unlocked_at.{badge_id}": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            },
        },
        upsert=True,
    )

    return True