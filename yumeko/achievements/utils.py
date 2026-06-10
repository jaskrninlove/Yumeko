# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
# ==========================================================

from pyrogram.enums import ParseMode

from yumeko.core.database import users_col
from yumeko.achievements.badges import get_badge
from yumeko.achievements.db import unlock_badge
from yumeko.achievements.strings import badge_unlocked_text


async def notify_badge(client, chat_id: int, user_id: int, badge_id: str):
    unlocked = await unlock_badge(user_id, badge_id)

    if not unlocked:
        return False

    badge = get_badge(badge_id)

    if not badge:
        return False

    # Send achievement only in user's DM, not in group.
    try:
        await client.send_message(
            user_id,
            badge_unlocked_text(badge["name"]),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
    except Exception:
        # User may not have started bot in DM. Ignore silently to avoid group spam.
        pass

    return True


async def check_basic_achievements(client, chat_id: int, user_id: int):
    user = await users_col.find_one({"user_id": user_id})

    if not user:
        return []

    unlocked = []

    if await notify_badge(client, chat_id, user_id, "first_steps"):
        unlocked.append("first_steps")

    if user.get("games_won", 0) >= 1:
        if await notify_badge(client, chat_id, user_id, "first_win"):
            unlocked.append("first_win")

    if user.get("coins", 0) >= 10000:
        if await notify_badge(client, chat_id, user_id, "rich_player"):
            unlocked.append("rich_player")

    return unlocked


async def check_marriage_achievement(client, chat_id: int, user_id: int):
    return await notify_badge(client, chat_id, user_id, "married_soul")


async def check_shop_achievement(client, chat_id: int, user_id: int):
    return await notify_badge(client, chat_id, user_id, "shopper")


async def check_pet_achievement(client, chat_id: int, user_id: int):
    return await notify_badge(client, chat_id, user_id, "pet_lover")


async def check_love_achievement(client, chat_id: int, user_id: int, love_points: int):
    if love_points >= 500:
        return await notify_badge(client, chat_id, user_id, "love_master")
    return False


async def check_gambler_achievement(client, chat_id: int, user_id: int):
    return await notify_badge(client, chat_id, user_id, "gambler")