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

from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message

from yumeko.client import app
from yumeko.database.users import add_user, get_user
from yumeko.helpers.buttons import back_home_buttons
from yumeko.shop.shop_db import get_inventory
from yumeko.shop.items import TITLES, PETS
from yumeko.achievements.db import get_user_achievements
from yumeko.social.marriage_db import get_profile_marriage, days_together
from yumeko.core.database import users_col


def get_level(xp: int):
    return max(1, xp // 500 + 1)


def get_rank_title(level: int):
    if level >= 50:
        return "👑 Arcade Royal"
    if level >= 30:
        return "💎 Elite Gambler"
    if level >= 20:
        return "🎰 High Roller"
    if level >= 10:
        return "♠️ Risk Taker"
    if level >= 5:
        return "🎭 Rising Player"
    return "🌸 New Player"


def make_progress_bar(xp: int):
    current = xp % 500
    filled = current // 50
    empty = 10 - filled
    return "▰" * filled + "▱" * empty, current, 500


def get_partner_name(marriage: dict, user_id: int):
    if not marriage:
        return "Not married"

    u1 = marriage.get("user1", {})
    u2 = marriage.get("user2", {})

    if u1.get("id") == user_id:
        return u2.get("name", "Unknown")

    return u1.get("name", "Unknown")


async def build_profile_text(user, data: dict, chat_id: int | None = None):
    coins = data.get("coins", 0)
    xp = data.get("xp", 0)

    games_played = data.get("games_played", 0)
    games_won = data.get("games_won", 0)
    games_lost = data.get("games_lost", 0)

    win_rate = 0
    if games_played:
        win_rate = round((games_won / games_played) * 100, 2)

    mafia_games = data.get("mafia_games", 0)
    mafia_wins = data.get("mafia_wins", 0)
    mafia_losses = data.get("mafia_losses", 0)
    mafia_jester_wins = data.get("mafia_jester_wins", 0)

    mafia_rate = 0
    if mafia_games:
        mafia_rate = round((mafia_wins / mafia_games) * 100, 2)

    level = get_level(xp)
    rank_title = get_rank_title(level)
    bar, current_xp, needed_xp = make_progress_bar(xp)

    inv = await get_inventory(user.id)

    active_title_id = inv.get("active_title")
    active_pet_id = inv.get("active_pet")

    active_title = TITLES.get(active_title_id, {}).get("name", "None")
    active_pet = PETS.get(active_pet_id, {}).get("name", "None")

    achievements = await get_user_achievements(user.id)
    badges_count = len(achievements.get("badges", []))

    marriage = await get_profile_marriage(user.id, chat_id)
    partner = get_partner_name(marriage, user.id)

    love_points = marriage.get("love_points", 0) if marriage else 0
    together = days_together(marriage.get("married_at")) if marriage else 0

    marriage_line = partner
    if marriage:
        marriage_line = f"{partner} · {together} days"

    return (
        f"<blockquote>🎭 <b>{user.first_name or 'Player'}'s Arcade Profile</b></blockquote>\n\n"
        f"<i>❝ Every game leaves a mark on the soul, darling. ♡ ❞</i>\n\n"

        f"<blockquote>👤 <b>Identity</b></blockquote>\n"
        f"👤 <b>Name:</b> {user.first_name or 'Unknown'}\n"
        f"🆔 <b>ID:</b> <code>{user.id}</code>\n"
        f"🌟 <b>Rank:</b> {rank_title}\n"
        f"⭐ <b>Level:</b> <code>{level}</code>\n\n"

        f"<blockquote>💎 <b>Progress & Wealth</b></blockquote>\n"
        f"💰 <b>Coins:</b> <code>{coins:,}</code>\n"
        f"✨ <b>XP:</b> <code>{xp:,}</code>\n"
        f"📊 <b>Progress:</b> <code>{bar}</code> <b>{current_xp}/{needed_xp}</b>\n\n"

        f"<blockquote>🎖 <b>Collection</b></blockquote>\n"
        f"🎖 <b>Active Title:</b> {active_title}\n"
        f"🐾 <b>Active Pet:</b> {active_pet}\n"
        f"🏅 <b>Badges:</b> <code>{badges_count}</code>\n\n"

        f"<blockquote>💞 <b>Romance</b></blockquote>\n"
        f"💞 <b>Married To:</b> {marriage_line}\n"
        f"❤️ <b>Love Points:</b> <code>{love_points}</code>\n\n"

        f"<blockquote>🎮 <b>Arcade Statistics</b></blockquote>\n"
        f"🎮 <b>Games Played:</b> <code>{games_played}</code>\n"
        f"🏆 <b>Wins:</b> <code>{games_won}</code>\n"
        f"💔 <b>Losses:</b> <code>{games_lost}</code>\n"
        f"📈 <b>Win Rate:</b> <code>{win_rate}%</code>\n\n"

        f"<blockquote>🎭 <b>Mafia Statistics</b></blockquote>\n"
        f"🎮 <b>Games Played:</b> <code>{mafia_games}</code>\n"
        f"🏆 <b>Wins:</b> <code>{mafia_wins}</code>\n"
        f"💀 <b>Losses:</b> <code>{mafia_losses}</code>\n"
        f"🤡 <b>Jester Wins:</b> <code>{mafia_jester_wins}</code>\n"
        f"📈 <b>Win Rate:</b> <code>{mafia_rate}%</code>\n\n"

        f"<i>Keep playing to climb Yumeko's world. ♡</i>"
    )


@app.on_message(filters.command(["profile", "me"]) & (filters.private | filters.group))
async def profile_cmd(_, message: Message):
    user = message.from_user

    if not user:
        return

    await add_user(user)

    await users_col.update_one(
        {"user_id": user.id},
        {
            "$set": {
                "last_chat_id": message.chat.id,
                "name": user.first_name or "Unknown",
                "username": user.username,
            }
        },
        upsert=True,
    )

    data = await get_user(user.id)

    chat_id = None
    if message.chat.type.name in ["GROUP", "SUPERGROUP"]:
        chat_id = message.chat.id
    else:
        chat_id = data.get("last_chat_id")

    text = await build_profile_text(user, data, chat_id)

    await message.reply_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=back_home_buttons(),
        disable_web_page_preview=True,
    )