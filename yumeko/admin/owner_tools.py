# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
# ==========================================================

import os
import time
import asyncio
import platform
from datetime import datetime

from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message

from yumeko.config import config
from yumeko.core.database import db, users_col


START_TIME = time.time()


def is_owner(user_id: int) -> bool:
    owners = getattr(config, "OWNER_ID", None) or getattr(config, "OWNER_IDS", None)

    if isinstance(owners, int):
        return user_id == owners

    if isinstance(owners, str):
        return str(user_id) in owners.replace(",", " ").split()

    if isinstance(owners, list):
        return user_id in owners or str(user_id) in owners

    return False


def uptime_text():
    seconds = int(time.time() - START_TIME)
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return f"{days}d {hours}h {minutes}m {seconds}s"


async def health_cmd(client, message: Message):
    if not message.from_user or not is_owner(message.from_user.id):
        return

    users = await users_col.count_documents({})
    groups = await db["groups"].count_documents({})

    try:
        commands = await users_col.aggregate([
            {"$group": {"_id": None, "total": {"$sum": "$commands_used"}}}
        ]).to_list(length=1)
        commands_used = commands[0]["total"] if commands else 0
    except Exception:
        commands_used = 0

    text = (
        "<blockquote>🩺 <b>Yumeko Health</b></blockquote>\n\n"
        "<i>❝ The arcade is breathing beautifully, darling. ♡ ❞</i>\n\n"
        f"⏳ <b>Uptime:</b> <code>{uptime_text()}</code>\n"
        f"🐍 <b>Python:</b> <code>{platform.python_version()}</code>\n"
        f"💻 <b>System:</b> <code>{platform.system()}</code>\n\n"
        f"👤 <b>Total Users:</b> <code>{users}</code>\n"
        f"🏰 <b>Total Groups:</b> <code>{groups}</code>\n"
        f"🎮 <b>Commands Used:</b> <code>{commands_used}</code>\n\n"
        f"🗄 <b>Database:</b> <code>Connected</code>\n"
        f"⚙️ <b>Status:</b> <code>Online</code>"
    )

    await message.reply_text(text, parse_mode=ParseMode.HTML)


async def active_cmd(client, message: Message):
    if not message.from_user or not is_owner(message.from_user.id):
        return

    users = await users_col.count_documents({})
    groups = await db["groups"].count_documents({})

    top_users = await users_col.find({}).sort("updated_at", -1).limit(5).to_list(length=5)

    lines = []
    for i, user in enumerate(top_users, start=1):
        name = user.get("name") or user.get("first_name") or "Unknown"
        xp = user.get("xp", 0)
        coins = user.get("coins", 0)
        lines.append(f"{i}. <b>{name}</b> — ✨ {xp} XP · 💰 {coins}")

    text = (
        "<blockquote>🎭 <b>Yumeko Activity</b></blockquote>\n\n"
        "<i>❝ Every player leaves a footprint inside my arcade. ♡ ❞</i>\n\n"
        f"👤 <b>Users:</b> <code>{users}</code>\n"
        f"🏰 <b>Groups:</b> <code>{groups}</code>\n"
        f"⏳ <b>Bot Uptime:</b> <code>{uptime_text()}</code>\n\n"
        "<b>Recently Active Players:</b>\n"
        f"{chr(10).join(lines) if lines else 'No users found.'}"
    )

    await message.reply_text(text, parse_mode=ParseMode.HTML)


async def broadcast_cmd(client, message: Message):
    if not message.from_user or not is_owner(message.from_user.id):
        return

    if not message.reply_to_message and len(message.command) < 2:
        await message.reply_text(
            "Reply to a message with <code>/broadcast</code> or use <code>/broadcast text</code>.",
            parse_mode=ParseMode.HTML,
        )
        return

    sent = 0
    failed = 0

    status = await message.reply_text("🎭 Broadcast started...")

    cursor = users_col.find({}, {"user_id": 1})

    async for user in cursor:
        try:
            if message.reply_to_message:
                await message.reply_to_message.copy(user["user_id"])
            else:
                text = message.text.split(None, 1)[1]
                await client.send_message(user["user_id"], text)
            sent += 1
            await asyncio.sleep(0.05)
        except Exception:
            failed += 1

    await status.edit_text(
        (
            "<blockquote>📢 <b>Broadcast Finished</b></blockquote>\n\n"
            f"✅ Sent: <code>{sent}</code>\n"
            f"❌ Failed: <code>{failed}</code>"
        ),
        parse_mode=ParseMode.HTML,
    )


def register_owner_tools(app):
    app.add_handler(MessageHandler(health_cmd, filters.command("health")), group=300)
    app.add_handler(MessageHandler(active_cmd, filters.command(["active", "activeusers"])), group=300)
    app.add_handler(MessageHandler(broadcast_cmd, filters.command(["broadcast", "gcast"])), group=300)