# ==========================================================
#  Yumeko Games Bot — Racing WebApp Handler
#  Copyright (c) 2026 Jass
# ==========================================================

import json
import urllib.parse
from pyrogram import Client, filters
from pyrogram.enums import ChatType, ParseMode
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from yumeko.config import config
from yumeko.database.users import add_user, add_coins, add_xp

def racing_url(chat_id: int, user_id: int) -> str:
    base = getattr(config, "RACING_WEBAPP_URL", "https://yumeko-racing.vercel.app/").rstrip("/")
    params = urllib.parse.urlencode({"chat": str(chat_id), "user": str(user_id)})
    return f"{base}/?{params}"

def racing_button(chat_id: int, user_id: int):
    return InlineKeyboardMarkup([[InlineKeyboardButton("🏎 Open Racing Track", web_app=WebAppInfo(url=racing_url(chat_id, user_id)))]])

async def racing_cmd(client: Client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        await message.reply_text("🏎 Racing works best from groups.")
        return
    if not message.from_user:
        return
    await add_user(message.from_user)
    await message.reply_text(
        "<blockquote>🏎 <b>Yumeko Racing</b></blockquote>\n\n"
        "Full-screen endless racing. Swipe left/right, double tap for nitro, dodge traffic and collect coins.\n\n"
        "🛣 Maps change as your level rises\n🏆 Submit score after crashing\n🔥 Higher distance = better rewards\n\n"
        "<i>❝ The road never ends, darling~ ♡ ❞</i>",
        reply_markup=racing_button(message.chat.id, message.from_user.id),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

async def racing_webapp_data(client: Client, message: Message):
    data = getattr(message, "web_app_data", None)
    if not data or not message.from_user:
        return
    try:
        payload = json.loads(data.data)
    except Exception:
        return
    if payload.get("type") != "racing_score":
        return
    user_id = message.from_user.id
    score = int(payload.get("score", 0))
    coins_collected = int(payload.get("coins", 0))
    distance = int(payload.get("distance", 0))
    level = int(payload.get("level", 1))
    chat_id = int(payload.get("chat_id", 0))
    reward_coins = min(700, 25 + coins_collected * 6 + score // 180)
    reward_xp = min(300, 12 + level * 6 + distance // 110)
    await add_coins(user_id, reward_coins)
    await add_xp(user_id, reward_xp)
    text = (
        "<blockquote>🏁 <b>Racing Score Submitted</b></blockquote>\n\n"
        f"👤 <a href=\"tg://user?id={user_id}\"><b>{message.from_user.first_name}</b></a>\n"
        f"🏆 Score: <b>{score}</b>\n🛣 Distance: <b>{distance}m</b>\n🔥 Level: <b>{level}</b>\n"
        f"🪙 Coins Collected: <b>{coins_collected}</b>\n\n"
        "<blockquote>🎁 <b>Rewards</b></blockquote>\n\n"
        f"🪙 +<b>{reward_coins}</b> Coins\n⭐ +<b>{reward_xp}</b> XP"
    )
    if chat_id:
        await client.send_message(chat_id, text, parse_mode=ParseMode.HTML)
    else:
        await message.reply_text(text, parse_mode=ParseMode.HTML)

def register_racing_webapp_handlers(app: Client):
    app.add_handler(MessageHandler(racing_cmd, filters.command(["race", "racing", "carrace"]) & filters.group), group=410)
    app.add_handler(MessageHandler(racing_webapp_data, filters.private), group=410)
