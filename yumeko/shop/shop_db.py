# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
#
#  Developer  : Jass
#  Project    : Yumeko Games Bot
#  Version    : 1.0.0
# ==========================================================

from yumeko.core.database import db, users_col


inventory_col = db["inventory"]


async def get_inventory(user_id: int):
    inv = await inventory_col.find_one({"user_id": user_id})

    if not inv:
        inv = {
            "user_id": user_id,
            "titles": [],
            "pets": [],
            "active_title": None,
            "active_pet": None,
        }
        await inventory_col.insert_one(inv)

    return inv


async def user_has_item(user_id: int, category: str, item_id: str):
    inv = await get_inventory(user_id)
    key = "titles" if category == "title" else "pets"
    return item_id in inv.get(key, [])


async def add_item(user_id: int, category: str, item_id: str):
    await get_inventory(user_id)
    key = "titles" if category == "title" else "pets"

    await inventory_col.update_one(
        {"user_id": user_id},
        {"$addToSet": {key: item_id}},
    )


async def set_active_item(user_id: int, category: str, item_id: str):
    await get_inventory(user_id)

    field = "active_title" if category == "title" else "active_pet"

    await inventory_col.update_one(
        {"user_id": user_id},
        {"$set": {field: item_id}},
    )


async def get_user_coins(user_id: int):
    user = await users_col.find_one({"user_id": user_id})

    if not user:
        return 0

    return user.get("coins", 0)


async def remove_user_coins(user_id: int, amount: int):
    await users_col.update_one(
        {"user_id": user_id},
        {"$inc": {"coins": -amount}},
    )