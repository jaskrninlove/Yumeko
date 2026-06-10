# ==========================================================
#  Yumeko Games Bot — Hot Potato Handler
#  Copyright (c) 2026 Jass  |  Version 2.0.1
# ==========================================================

import asyncio
import random

from pyrogram import Client, filters
from pyrogram.enums import ChatType, ParseMode
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.types import Message, CallbackQuery

from yumeko.database.users import add_user
from yumeko.database.groups import add_group
from yumeko.games.hot_potato import strings as S
from yumeko.games.hot_potato.game import (
    create_game,
    get_game,
    end_game,
    join_game,
    format_players,
    alive_players,
    pass_button,
    join_buttons,
    run_game,
    MIN_PLAYERS,
    JOIN_TIMEOUT,
)


async def cmd_hotpotato(client: Client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        await message.reply_text("🥔 Hot Potato can only be played in groups.")
        return

    if not message.from_user:
        return

    await add_user(message.from_user)
    await add_group(message.chat)

    chat_id = message.chat.id
    user = message.from_user

    if get_game(chat_id):
        await message.reply_text(S.ALREADY_RUNNING)
        return

    create_game(chat_id, user.id, user.first_name or "Unknown")
    join_game(chat_id, user)
    game = get_game(chat_id)

    msg = await message.reply_text(
        S.lobby_text(
            user.first_name or "Unknown",
            format_players(game),
            len(game["players"]),
            JOIN_TIMEOUT,
        ),
        reply_markup=join_buttons(),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

    await asyncio.sleep(JOIN_TIMEOUT)

    game = get_game(chat_id)

    if not game or game["status"] != "joining":
        return

    if len(game["players"]) < MIN_PLAYERS:
        end_game(chat_id)
        await msg.edit_text(
            S.NOT_ENOUGH,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
        return

    game["status"] = "starting"
    await _launch(client, msg, chat_id)


async def _launch(client: Client, message: Message, chat_id: int):
    game = get_game(chat_id)

    if not game:
        return

    await message.edit_text(
        (
            "<blockquote>🥔 <b>Game Starting!</b></blockquote>\n\n"
            "<i>❝ Ahahaha~ The potato is being heated~ ♡ ❞</i>\n\n"
            f"👥 <b>{len(game['players'])} players locked in</b>\n\n"
            f"{format_players(game)}\n\n"
            "<i>3... 2... 1... 🥔</i>"
        ),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

    await asyncio.sleep(3)
    await run_game(client, message, chat_id)


async def cb_hp_join(client: Client, callback: CallbackQuery):
    if not callback.message:
        return

    await add_user(callback.from_user)

    chat_id = callback.message.chat.id
    user = callback.from_user
    game = get_game(chat_id)

    if not game:
        await callback.answer("❌ No active game.", show_alert=True)
        return

    ok, reason = join_game(chat_id, user)

    if not ok:
        msgs = {
            "started": "⚡ Already started~",
            "full": S.GAME_FULL,
            "joined": S.ALREADY_JOINED,
        }
        await callback.answer(msgs.get(reason, "❌ Cannot join."), show_alert=True)
        return

    await callback.answer("🥔 Joined! Don't get burned~ ♡", show_alert=False)

    game = get_game(chat_id)

    await callback.message.edit_text(
        S.lobby_text(
            game["host_name"],
            format_players(game),
            len(game["players"]),
            JOIN_TIMEOUT,
        ),
        reply_markup=join_buttons(),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


async def cb_hp_start(client: Client, callback: CallbackQuery):
    if not callback.message:
        return

    chat_id = callback.message.chat.id
    user = callback.from_user
    game = get_game(chat_id)

    if not game:
        await callback.answer("❌ No game.", show_alert=True)
        return

    if user.id != game["host_id"]:
        await callback.answer(S.HOST_ONLY, show_alert=True)
        return

    if game["status"] != "joining":
        await callback.answer("⚡ Already running~", show_alert=True)
        return

    if len(game["players"]) < MIN_PLAYERS:
        await callback.answer(S.NOT_ENOUGH, show_alert=True)
        return

    await callback.answer("🥔 Starting~ ♡", show_alert=False)

    game["status"] = "starting"
    await _launch(client, callback.message, chat_id)


async def cb_hp_cancel(client: Client, callback: CallbackQuery):
    if not callback.message:
        return

    chat_id = callback.message.chat.id
    game = get_game(chat_id)

    if not game:
        await callback.answer("❌ No game.", show_alert=True)
        return

    if callback.from_user.id != game["host_id"]:
        await callback.answer(S.HOST_ONLY, show_alert=True)
        return

    end_game(chat_id)

    await callback.answer("❌ Cancelled.", show_alert=False)
    await callback.message.edit_text(
        S.GAME_CANCELLED,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


async def cb_hp_pass(client: Client, callback: CallbackQuery):
    if not callback.message:
        return

    chat_id = callback.message.chat.id
    user_id = callback.from_user.id
    game = get_game(chat_id)

    if not game or game["status"] != "running":
        await callback.answer("❌ No active game.", show_alert=False)
        return

    if user_id != game.get("holder_id"):
        await callback.answer(S.NOT_YOUR_POTATO, show_alert=True)
        return

    alive = alive_players(game)
    candidates = [uid for uid in alive if uid != user_id]

    if not candidates:
        await callback.answer("No one to pass to~", show_alert=True)
        return

    new_holder = random.choice(candidates)

    old_name = game["players"][user_id]["name"]
    new_name = game["players"][new_holder]["name"]

    game["holder_id"] = new_holder
    game["pass_count"] += 1

    await callback.answer(f"🥔 Passed to {new_name}~ ♡", show_alert=False)

    await callback.message.edit_text(
        S.passed_text(old_name, new_name)
        + "\n\n"
        + S.potato_holder_text(
            new_name,
            game["pass_count"],
            {
                p["name"]: p["lives"]
                for p in game["players"].values()
                if p["alive"]
            },
        ),
        reply_markup=pass_button(game),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


def register_hot_potato_handlers(app: Client):
    app.add_handler(
        MessageHandler(
            cmd_hotpotato,
            filters.command(["hotpotato", "potato"]) & filters.group,
        ),
        group=360,
    )

    app.add_handler(
        CallbackQueryHandler(
            cb_hp_join,
            filters.regex("^hp_join$"),
        ),
        group=360,
    )

    app.add_handler(
        CallbackQueryHandler(
            cb_hp_start,
            filters.regex("^hp_start$"),
        ),
        group=360,
    )

    app.add_handler(
        CallbackQueryHandler(
            cb_hp_cancel,
            filters.regex("^hp_cancel$"),
        ),
        group=360,
    )

    app.add_handler(
        CallbackQueryHandler(
            cb_hp_pass,
            filters.regex("^hp_pass$"),
        ),
        group=360,
    )