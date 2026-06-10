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

from functools import wraps
from pyrogram.enums import ChatMemberStatus, ChatType

from yumeko.config import config


async def is_admin(client, chat_id: int, user_id: int) -> bool:
    if user_id == config.OWNER_ID:
        return True

    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in (
            ChatMemberStatus.OWNER,
            ChatMemberStatus.ADMINISTRATOR,
        )
    except Exception:
        return False


async def is_bot_admin(client, chat_id: int) -> bool:
    try:
        me = await client.get_me()
        member = await client.get_chat_member(chat_id, me.id)
        return member.status in (
            ChatMemberStatus.OWNER,
            ChatMemberStatus.ADMINISTRATOR,
        )
    except Exception:
        return False


def admin_only(func):
    @wraps(func)
    async def wrapper(client, message):
        if message.chat.type == ChatType.PRIVATE:
            return await func(client, message)

        user = message.from_user
        if not user:
            return

        if not await is_admin(client, message.chat.id, user.id):
            return await message.reply_text(
                "Only group admins can use this command."
            )

        return await func(client, message)

    return wrapper


def bot_admin_required(func):
    @wraps(func)
    async def wrapper(client, message):
        if message.chat.type == ChatType.PRIVATE:
            return await func(client, message)

        if not await is_bot_admin(client, message.chat.id):
            return await message.reply_text(
                "Please make me admin first, otherwise I cannot manage games properly."
            )

        return await func(client, message)

    return wrapper