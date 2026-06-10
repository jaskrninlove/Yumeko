# ==========================================================
#  Yumeko Games Bot — Message Handler
#  Copyright (c) 2026 Jass  |  Version 3.0.0
# ==========================================================

import asyncio
import os
import time
import html
import random
from pyrogram import filters
from pyrogram.enums import ChatType, ParseMode
from pyrogram.errors import FloodWait, MessageNotModified
from pyrogram.types import Message, CallbackQuery

from yumeko.client import app
from yumeko.config import config
from yumeko.core.notifier import send_log
from yumeko.database.users import add_user
from yumeko.database.groups import add_group
from yumeko.helpers.buttons import (
    start_buttons,
    group_start_buttons,
    group_added_buttons,
    games_menu_buttons,
    games_page_buttons,
    game_info_buttons,
    game_detail_buttons,
    back_home_buttons,
    games_page_caption,
    game_info_caption,
    game_command_caption,
    game_help_caption,
    game_rules_caption,
    game_rewards_caption,
)
from yumeko.locales import get_text


START_TIME = time.time()


def get_uptime():
    s = int(time.time() - START_TIME)
    d, s = divmod(s, 86400)
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)

    if d:
        return f"{d}d {h}h {m}m"
    if h:
        return f"{h}h {m}m {s}s"
    if m:
        return f"{m}m {s}s"
    return f"{s}s"


async def safe_edit(message, text, reply_markup=None):
    try:
        return await message.edit_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup,
            disable_web_page_preview=True,
        )
    except MessageNotModified:
        return None
    except FloodWait as e:
        await asyncio.sleep(e.value + 1)
        try:
            return await message.edit_text(
                text,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup,
                disable_web_page_preview=True,
            )
        except Exception:
            return None
    except Exception:
        return None


async def make_start_caption(user):
    bot = await app.get_me()

    safe_name = html.escape(user.first_name or "Player") if user else "Player"
    mention = (
        f'<a href="tg://user?id={user.id}">{safe_name}</a>'
        if user
        else safe_name
    )

    return get_text(
        "start_caption",
        mention=mention,
        first_name=safe_name,
        bot_name=html.escape(bot.first_name or "Yumeko"),
    )


async def send_start(message: Message):
    if message.chat.type == ChatType.PRIVATE:
        caption = await make_start_caption(message.from_user)

        if os.path.exists(config.START_IMAGE):
            await message.reply_photo(
                photo=config.START_IMAGE,
                caption=caption,
                parse_mode=ParseMode.HTML,
                reply_markup=start_buttons(),
            )
        else:
            await message.reply_text(
                caption,
                parse_mode=ParseMode.HTML,
                reply_markup=start_buttons(),
                disable_web_page_preview=True,
            )
        return

    await add_group(message.chat)

    await message.reply_text(
        get_text("group_start_caption"),
        parse_mode=ParseMode.HTML,
        reply_markup=group_start_buttons(),
        disable_web_page_preview=True,
    )


@app.on_message(filters.command("start"))
async def start_cmd(_, message: Message):
    user = message.from_user
    chat = message.chat

    if chat.type != ChatType.PRIVATE:
        await add_group(chat)
        try:
            await message.delete()
        except Exception:
            pass
        return

    if not user:
        return

    is_new = await add_user(user)

    await send_log(
        app,
        get_text(
            "new_user_log" if is_new else "old_user_log",
            name=user.first_name or "Unknown",
            user_id=user.id,
            username=user.username or "None",
        ),
    )

    await send_start(message)


@app.on_message(filters.command(["games", "game"]))
async def games_cmd(_, message: Message):
    await message.reply_text(
        games_page_caption("all", 0),
        parse_mode=ParseMode.HTML,
        reply_markup=games_page_buttons("all", 0),
        disable_web_page_preview=True,
    )


@app.on_message(filters.command("help"))
async def help_cmd(_, message: Message):
    await message.reply_text(
        get_text("help_caption"),
        parse_mode=ParseMode.HTML,
        reply_markup=back_home_buttons(),
        disable_web_page_preview=True,
    )


@app.on_message(filters.command("ping"))
async def ping_cmd(_, message: Message):
    t = time.time()
    sent = await message.reply_text("🏓")
    ping = round((time.time() - t) * 1000, 2)

    await sent.edit_text(
        get_text("ping_caption", ping=ping, uptime=get_uptime()),
        parse_mode=ParseMode.HTML,
    )


@app.on_callback_query(filters.regex("^start_home$"))
async def cb_start_home(_, query: CallbackQuery):
    caption = await make_start_caption(query.from_user)

    await safe_edit(
        query.message,
        caption,
        reply_markup=start_buttons(),
    )

    await query.answer()


@app.on_callback_query(filters.regex("^games_menu$"))
async def cb_games_menu(_, query: CallbackQuery):
    flavors = [
        "Choose your table, darling. ♡",
        "So many ways to lose yourself here. ♡",
        "Every game is a gamble. Which one calls to you? ♡",
    ]

    await safe_edit(
        query.message,
        (
            "<blockquote>🎮 <b>Yumeko Arcade — Categories</b></blockquote>\n\n"
            f"<i>❝ {random.choice(flavors)} ❞</i>"
        ),
        reply_markup=games_menu_buttons(),
    )

    await query.answer()


@app.on_callback_query(filters.regex(r"^games_page_"))
async def cb_games_page(_, query: CallbackQuery):
    data = query.data.replace("games_page_", "", 1)

    try:
        category_id, page = data.rsplit("_", 1)
        page = int(page)
    except Exception:
        category_id, page = "all", 0

    await safe_edit(
        query.message,
        games_page_caption(category_id, page),
        reply_markup=games_page_buttons(category_id, page),
    )

    await query.answer()


@app.on_callback_query(filters.regex(r"^gameinfo_"))
async def cb_game_info(_, query: CallbackQuery):
    game_id = query.data.replace("gameinfo_", "", 1)

    await safe_edit(
        query.message,
        game_info_caption(game_id),
        reply_markup=game_info_buttons(game_id),
    )

    await query.answer()


@app.on_callback_query(filters.regex(r"^gamecmd_"))
async def cb_game_cmd(_, query: CallbackQuery):
    game_id = query.data.replace("gamecmd_", "", 1)

    await safe_edit(
        query.message,
        game_command_caption(game_id),
        reply_markup=game_detail_buttons(game_id),
    )

    await query.answer()


@app.on_callback_query(filters.regex(r"^gamehelp_"))
async def cb_game_help(_, query: CallbackQuery):
    game_id = query.data.replace("gamehelp_", "", 1)

    await safe_edit(
        query.message,
        game_help_caption(game_id),
        reply_markup=game_detail_buttons(game_id),
    )

    await query.answer()


@app.on_callback_query(filters.regex(r"^gamerules_"))
async def cb_game_rules(_, query: CallbackQuery):
    game_id = query.data.replace("gamerules_", "", 1)

    await safe_edit(
        query.message,
        game_rules_caption(game_id),
        reply_markup=game_detail_buttons(game_id),
    )

    await query.answer()


@app.on_callback_query(filters.regex(r"^gamerewards_"))
async def cb_game_rewards(_, query: CallbackQuery):
    game_id = query.data.replace("gamerewards_", "", 1)

    await safe_edit(
        query.message,
        game_rewards_caption(game_id),
        reply_markup=game_detail_buttons(game_id),
    )

    await query.answer()


@app.on_callback_query(filters.regex("^help_menu$"))
async def cb_help_menu(_, query: CallbackQuery):
    await safe_edit(
        query.message,
        get_text("help_caption"),
        reply_markup=back_home_buttons(),
    )

    await query.answer()


@app.on_callback_query(filters.regex("^owner_menu$"))
async def cb_owner_menu(_, query: CallbackQuery):
    await safe_edit(
        query.message,
        get_text("owner_caption"),
        reply_markup=back_home_buttons(),
    )

    await query.answer()


@app.on_message(filters.new_chat_members)
async def bot_added(_, message: Message):
    for member in message.new_chat_members:
        if not member.is_self:
            continue

        await add_group(message.chat)

        await send_log(
            app,
            get_text(
                "new_group_log",
                title=message.chat.title or "Unknown",
                chat_id=message.chat.id,
                username=message.chat.username or "None",
            ),
        )

        await message.reply_text(
            get_text("bot_added_caption"),
            parse_mode=ParseMode.HTML,
            reply_markup=group_added_buttons(),
            disable_web_page_preview=True,
        )