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
from yumeko.shop.shop_db import get_inventory


pets_col = db["pets"]


async def get_pet_profile(user_id: int):
    inv = await get_inventory(user_id)
    active_pet = inv.get("active_pet")

    if not active_pet:
        return None

    pet = await pets_col.find_one({"user_id": user_id, "pet_id": active_pet})

    if not pet:
        pet = {
            "user_id": user_id,
            "pet_id": active_pet,
            "level": 1,
            "xp": 0,
            "hunger": 50,
            "last_feed": None,
            "created_at": datetime.utcnow(),
        }
        await pets_col.insert_one(pet)

    return pet


async def feed_pet(user_id: int):
    pet = await get_pet_profile(user_id)

    if not pet:
        return None, "no_pet", None

    last_feed = pet.get("last_feed")

    if last_feed:
        next_feed = last_feed + timedelta(hours=6)

        if datetime.utcnow() < next_feed:
            remaining = next_feed - datetime.utcnow()
            h, rem = divmod(int(remaining.total_seconds()), 3600)
            m, _ = divmod(rem, 60)
            return pet, "cooldown", f"{h}h {m}m"

    gained_xp = 20
    new_xp = pet.get("xp", 0) + gained_xp
    level = pet.get("level", 1)

    while new_xp >= level * 100:
        new_xp -= level * 100
        level += 1

    hunger = min(pet.get("hunger", 50) + 25, 100)

    await pets_col.update_one(
        {"_id": pet["_id"]},
        {
            "$set": {
                "xp": new_xp,
                "level": level,
                "hunger": hunger,
                "last_feed": datetime.utcnow(),
            }
        },
    )

    pet["xp"] = new_xp
    pet["level"] = level
    pet["hunger"] = hunger

    return pet, "fed", gained_xp