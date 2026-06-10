# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
# ==========================================================

import asyncio

from pyrogram import filters
from pyrogram.enums import ChatType, ParseMode
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.types import Message, CallbackQuery

from yumeko.core.game_manager import is_game_running, get_running_game, lock_game, unlock_game
from yumeko.core.logger import game_started, game_finished
from yumeko.database.users import add_user
from yumeko.helpers.permissions import is_admin, is_bot_admin
from yumeko.locales import get_text

from yumeko.games.tictactoe.game import (
    JOIN_TIME,
    TURN_TIME,
    create_game,
    get_game,
    end_game,
    set_message,
    join_game,
    start_game,
    get_current_player,
    make_move,
    board_buttons,
    join_button,
    reward_win,
    reward_draw,
)

from yumeko.games.tictactoe.strings import (
    lobby_text,
    join_countdown_text,
    not_enough_players,
    game_start_text,
    turn_text,
    timeout_text,
    stop_text,
    draw_text,
    winner_text,
    rules_text,
)


async def tictactoe_cmd(client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        await message.reply_text("Tic Tac Toe can only be played in groups.")
        return

    chat_id = message.chat.id
    user = message.from_user

    if not user:
        return

    if not await is_admin(client, chat_id, user.id):
        await message.reply_text("Only group admins can start Tic Tac Toe.")
        return

    if not await is_bot_admin(client, chat_id):
        await message.reply_text("Please make me admin first, darling.")
        return

    if is_game_running(chat_id):
        await message.reply_text(
            get_text("game_already_running_global", game=get_running_game(chat_id)),
            parse_mode=ParseMode.HTML,
        )
        return

    await add_user(user)

    create_game(chat_id, user)
    lock_game(chat_id, "Tic Tac Toe")

    join_game(chat_id, user)
    game = get_game(chat_id)

    game_started("Tic Tac Toe", chat_id)

    sent = await message.reply_text(
        lobby_text(game),
        parse_mode=ParseMode.HTML,
        reply_markup=join_button(),
        disable_web_page_preview=True,
    )

    set_message(chat_id, sent.id)
    asyncio.create_task(join_countdown(client, chat_id))


async def ttt_rules_cmd(_, message: Message):
    await message.reply_text(
        rules_text(),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


async def update_lobby(client, chat_id: int):
    game = get_game(chat_id)

    if not game or not game.get("message_id"):
        return

    try:
        await client.edit_message_text(
            chat_id,
            game["message_id"],
            lobby_text(game),
            parse_mode=ParseMode.HTML,
            reply_markup=join_button(),
            disable_web_page_preview=True,
        )
    except Exception:
        pass


async def ttt_join_callback(client, query: CallbackQuery):
    chat_id = query.message.chat.id
    user = query.from_user

    game = get_game(chat_id)

    if not game or game["status"] != "joining":
        await query.answer("No open Tic Tac Toe duel.", show_alert=True)
        return

    if user.id == game["host_id"]:
        await query.answer("You are already seated as host.", show_alert=True)
        return

    await add_user(user)

    ok, reason = join_game(chat_id, user)

    if not ok:
        if reason == "already_joined":
            await query.answer("You're already seated.", show_alert=True)
        elif reason == "full":
            await query.answer("This duel already has two players.", show_alert=True)
        else:
            await query.answer("You cannot join now.", show_alert=True)
        return

    await query.answer("You accepted the duel.")
    await update_lobby(client, chat_id)

    if len(game["players"]) >= 2:
        await start_match(client, chat_id)


async def join_countdown(client, chat_id: int):
    await asyncio.sleep(max(JOIN_TIME - 15, 1))

    game = get_game(chat_id)

    if not game or game["status"] != "joining":
        return

    try:
        await client.send_message(
            chat_id,
            join_countdown_text(15),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
    except Exception:
        pass

    await asyncio.sleep(15)

    game = get_game(chat_id)

    if not game or game["status"] != "joining":
        return

    if len(game["players"]) < 2:
        await client.send_message(
            chat_id,
            not_enough_players(),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
        end_game(chat_id)
        unlock_game(chat_id)
        return

    await start_match(client, chat_id)


async def start_match(client, chat_id: int):
    game = get_game(chat_id)

    if not game or game["status"] != "joining":
        return

    start_game(chat_id)
    game = get_game(chat_id)

    await client.send_message(
        chat_id,
        game_start_text(game),
        parse_mode=ParseMode.HTML,
        reply_markup=board_buttons(game),
        disable_web_page_preview=True,
    )

    asyncio.create_task(turn_timeout(client, chat_id, game["turn_token"]))


async def turn_timeout(client, chat_id: int, token: int):
    await asyncio.sleep(TURN_TIME)

    game = get_game(chat_id)

    if not game or game["status"] != "running":
        return

    if token != game["turn_token"]:
        return

    current = get_current_player(game)

    if not current:
        return

    loser_id = current["id"]

    winner_id = None
    for uid in game["players"]:
        if uid != loser_id:
            winner_id = uid
            break

    if not winner_id:
        return

    await reward_win(chat_id, winner_id)

    await client.send_message(
        chat_id,
        timeout_text(current["name"]),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

    await client.send_message(
        chat_id,
        winner_text(game, winner_id),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

    game_finished("Tic Tac Toe", game["players"][winner_id]["name"])
    end_game(chat_id)
    unlock_game(chat_id)


async def ttt_move_callback(client, query: CallbackQuery):
    chat_id = query.message.chat.id
    user = query.from_user

    game = get_game(chat_id)

    if not game or game["status"] != "running":
        await query.answer("No active Tic Tac Toe duel.", show_alert=True)
        return

    index = int(query.data.replace("ttt_move_", "", 1))

    ok, result = make_move(chat_id, user.id, index)

    if not ok:
        if result == "not_player":
            await query.answer("You are not part of this duel.", show_alert=True)
        elif result == "not_turn":
            await query.answer("Not your turn, darling~", show_alert=True)
        elif result == "taken":
            await query.answer("That square is already taken.", show_alert=True)
        else:
            await query.answer("Invalid move.", show_alert=True)
        return

    game = get_game(chat_id)

    if result["type"] == "win":
        winner_id = result["winner"]

        await query.message.edit_text(
            winner_text(game, winner_id),
            parse_mode=ParseMode.HTML,
            reply_markup=board_buttons(game),
            disable_web_page_preview=True,
        )

        await reward_win(chat_id, winner_id)

        game_finished("Tic Tac Toe", game["players"][winner_id]["name"])
        end_game(chat_id)
        unlock_game(chat_id)
        await query.answer("Victory.")
        return

    if result["type"] == "draw":
        await query.message.edit_text(
            draw_text(game),
            parse_mode=ParseMode.HTML,
            reply_markup=board_buttons(game),
            disable_web_page_preview=True,
        )

        await reward_draw(chat_id)

        game_finished("Tic Tac Toe", "Draw")
        end_game(chat_id)
        unlock_game(chat_id)
        await query.answer("Draw.")
        return

    await query.message.edit_text(
        turn_text(game),
        parse_mode=ParseMode.HTML,
        reply_markup=board_buttons(game),
        disable_web_page_preview=True,
    )

    asyncio.create_task(turn_timeout(client, chat_id, game["turn_token"]))
    await query.answer("Move recorded.")


async def ttt_stop_callback(client, query: CallbackQuery):
    chat_id = query.message.chat.id
    user = query.from_user

    game = get_game(chat_id)

    if not game:
        await query.answer("No active Tic Tac Toe duel.", show_alert=True)
        return

    if user.id not in game["players"]:
        await query.answer("Only duel players can stop this game.", show_alert=True)
        return

    await query.message.edit_text(
        stop_text(user.first_name or "Unknown"),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

    end_game(chat_id)
    unlock_game(chat_id)
    await query.answer("Duel stopped.")


def register_tictactoe_handlers(app):
    app.add_handler(
        MessageHandler(
            tictactoe_cmd,
            filters.command(["tictactoe", "ttt"]) & filters.group,
        ),
        group=240,
    )

    app.add_handler(
        MessageHandler(
            ttt_rules_cmd,
            filters.command(["tttrules", "tictactoerules"]),
        ),
        group=240,
    )

    app.add_handler(
        CallbackQueryHandler(
            ttt_join_callback,
            filters.regex("^ttt_join$"),
        ),
        group=241,
    )

    app.add_handler(
        CallbackQueryHandler(
            ttt_move_callback,
            filters.regex("^ttt_move_"),
        ),
        group=241,
    )

    app.add_handler(
        CallbackQueryHandler(
            ttt_stop_callback,
            filters.regex("^ttt_stop$"),
        ),
        group=241,
    )