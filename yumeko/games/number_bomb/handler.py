# ==========================================================
#  Yumeko Games Bot — Number Bomb Handler
#  Copyright (c) 2026 Jass  |  Version 2.0.0
# ==========================================================

import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery

from yumeko.database.users import add_user
from yumeko.database.groups import add_group
from yumeko.games.number_bomb import strings as S
from yumeko.games.number_bomb.game import (
    create_game, get_game, end_game, join_game,
    format_players, alive_players, join_buttons,
    run_game, MIN_PLAYERS, JOIN_TIMEOUT,
)


def _is_group(_, __, m): return m.chat.type.name in ("GROUP","SUPERGROUP")
group_filter = filters.create(_is_group)


async def cmd_numberbomb(client: Client, message: Message):
    await add_user(message.from_user)
    await add_group(message.chat)
    chat_id = message.chat.id
    user    = message.from_user

    if get_game(chat_id):
        await message.reply_text(S.ALREADY_RUNNING); return

    create_game(chat_id, user.id, user.first_name)
    join_game(chat_id, user)
    game = get_game(chat_id)

    msg = await message.reply_text(
        S.lobby_text(user.first_name, format_players(game),
                     len(game["players"]), JOIN_TIMEOUT),
        reply_markup=join_buttons(),
    )

    await asyncio.sleep(JOIN_TIMEOUT)
    game = get_game(chat_id)
    if not game or game["status"] != "joining": return

    if len(game["players"]) < MIN_PLAYERS:
        end_game(chat_id)
        await msg.edit_text(S.NOT_ENOUGH_PLAYERS)
        return

    game["status"] = "starting"
    await _launch(client, msg, chat_id)


async def _launch(client, message, chat_id: int):
    game = get_game(chat_id)
    if not game: return
    await message.edit_text(
        S.lobby_updated(game["host_name"], format_players(game), len(game["players"]))
    )
    await asyncio.sleep(2)
    await run_game(client, message, chat_id)


async def cb_nb_join(client: Client, callback: CallbackQuery):
    await add_user(callback.from_user)
    chat_id = callback.message.chat.id
    user    = callback.from_user
    game    = get_game(chat_id)

    if not game:
        await callback.answer(S.NOT_IN_GAME, show_alert=True); return

    ok, reason = join_game(chat_id, user)
    msgs = {"started": S.NOT_IN_GAME, "full": S.GAME_FULL, "joined": S.ALREADY_JOINED}
    if not ok:
        await callback.answer(msgs.get(reason, "❌"), show_alert=True); return

    await callback.answer("💣 Joined! Stay calm and count.", show_alert=False)
    game = get_game(chat_id)
    await callback.message.edit_text(
        S.lobby_text(game["host_name"], format_players(game),
                     len(game["players"]), JOIN_TIMEOUT),
        reply_markup=join_buttons(),
    )


async def cb_nb_start(client: Client, callback: CallbackQuery):
    chat_id = callback.message.chat.id
    user    = callback.from_user
    game    = get_game(chat_id)

    if not game:
        await callback.answer("❌ No game.", show_alert=True); return
    if user.id != game["host_id"]:
        await callback.answer(S.HOST_ONLY, show_alert=True); return
    if game["status"] != "joining":
        await callback.answer("⚡ Already started~", show_alert=True); return
    if len(game["players"]) < MIN_PLAYERS:
        await callback.answer(S.NOT_ENOUGH_PLAYERS, show_alert=True); return

    await callback.answer("💣 Arming the bomb~  ♡", show_alert=False)
    game["status"] = "starting"
    await _launch(client, callback.message, chat_id)


async def cb_nb_cancel(client: Client, callback: CallbackQuery):
    chat_id = callback.message.chat.id
    game    = get_game(chat_id)

    if not game:
        await callback.answer("❌", show_alert=True); return
    if callback.from_user.id != game["host_id"]:
        await callback.answer(S.HOST_ONLY, show_alert=True); return

    end_game(chat_id)
    await callback.answer("❌ Cancelled.", show_alert=False)
    await callback.message.edit_text(S.GAME_CANCELLED)


async def on_number_message(client: Client, message: Message):
    """Handles player number inputs during the game."""
    chat_id = message.chat.id
    user_id = message.from_user.id
    game    = get_game(chat_id)

    if not game or game["status"] != "running": return
    if not game.get("waiting_input"):           return
    if user_id != game.get("expected_pid"):     return

    try:
        num = int(message.text.strip())
    except (ValueError, AttributeError):
        return

    expected = game.get("expected_num", 0)
    if num != expected: return  # wrong number — ignore, let timeout handle

    game["current_num"] = num

    # Check bomb
    if num == game["bomb_number"]:
        game["players"][user_id]["alive"] = False
        game["turn_order"] = [u for u in game["turn_order"]
                               if game["players"][u]["alive"]]
        game["turn_index"] = game["turn_index"] % max(1, len(game["turn_order"]))
        game["last_result"]    = "bomb"
        game["waiting_input"]  = False
    else:
        game["last_result"]   = "ok"
        game["waiting_input"] = False


def register_number_bomb_handlers(app: Client):
    app.on_message(filters.command(["numberbomb", "nb"]) & group_filter)(cmd_numberbomb)
    app.on_callback_query(filters.regex("^nb_join$"))(cb_nb_join)
    app.on_callback_query(filters.regex("^nb_start$"))(cb_nb_start)
    app.on_callback_query(filters.regex("^nb_cancel$"))(cb_nb_cancel)
    app.on_message(filters.text & group_filter)(on_number_message)