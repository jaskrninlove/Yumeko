# ==========================================================
#  Yumeko Games Bot — Fun Interaction Handler
#  Copyright (c) 2026 Jass
# ==========================================================

import html
import random

from pyrogram import filters
from pyrogram.enums import ChatType, ParseMode
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message

from yumeko.database.users import add_user
from yumeko.database.groups import add_group
from yumeko.games.fun.interactions import ACTIONS, get_action
from yumeko.games.fun.stickers import get_stickers


def mention(user, fallback: str = "Player") -> str:
    if not user:
        return html.escape(fallback)

    name = html.escape(user.first_name or fallback)

    if not getattr(user, "id", None):
        return name

    return f'<a href="tg://user?id={user.id}">{name}</a>'


def plain_name_from_sender(message: Message) -> str:
    if message.sender_chat:
        return html.escape(message.sender_chat.title or "Anonymous Admin")
    return "Anonymous Admin"


def build_interaction_text(action: str, user_text: str, target_text: str, mode: str = "normal"):
    data = get_action(action)

    if not data:
        return None

    if mode == "self":
        return data["self"].format(user=user_text, target=target_text)

    if mode == "bot":
        return data["bot"].format(user=user_text, target=target_text)

    template = random.choice(data["templates"])

    return (
        template.format(user=user_text, target=target_text)
        + f"\n\n{data['emoji']} <b>{data['score']}</b>"
    )


async def send_action_sticker(client, message: Message, action: str):
    stickers = get_stickers(action)

    if not stickers:
        return

    try:
        await client.send_sticker(
            chat_id=message.chat.id,
            sticker=random.choice(stickers),
            reply_to_message_id=(
                message.reply_to_message.id
                if message.reply_to_message
                else message.id
            ),
        )
    except Exception:
        pass


async def interaction_cmd(client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        await message.reply_text("🎭 Use this command in groups, darling~")
        return

    if not message.from_user:
        return

    await add_user(message.from_user)
    await add_group(message.chat)

    action = message.command[0].split("@")[0].lower()
    reply = message.reply_to_message

    user_text = mention(message.from_user)

    if not reply:
        await message.reply_text(
            f"🎭 Reply to someone with <code>/{action}</code>, darling~",
            parse_mode=ParseMode.HTML,
            reply_to_message_id=message.id,
        )
        return

    target_user = reply.from_user

    if not target_user:
        target_text = plain_name_from_sender(reply)
        mode = "normal"
    else:
        target_text = mention(target_user)

        if target_user.id == message.from_user.id:
            mode = "self"
        elif target_user.is_bot:
            mode = "bot"
        else:
            mode = "normal"

    text = build_interaction_text(
        action=action,
        user_text=user_text,
        target_text=target_text,
        mode=mode,
    )

    if not text:
        return

    await send_action_sticker(client, message, action)

    await message.reply_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_to_message_id=reply.id,
        disable_web_page_preview=True,
    )


def register_interaction_handlers(app):
    commands = list(ACTIONS.keys())

    app.add_handler(
        MessageHandler(
            interaction_cmd,
            filters.command(commands) & filters.group,
        ),
        group=200,
    )