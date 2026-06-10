# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
# ==========================================================

import asyncio

from pyrogram import filters
from pyrogram.enums import ChatType, ParseMode
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.types import Message, CallbackQuery

from yumeko.helpers.word_dictionary import clean_word, is_valid_dictionary_word
from yumeko.core.game_manager import is_game_running, get_running_game, lock_game, unlock_game
from yumeko.core.logger import game_started, game_finished
from yumeko.database.users import add_user
from yumeko.games.bomb_party.game import (
    TURN_TIME,
    MIN_PLAYERS,
    create_game,
    get_game,
    end_game,
    join_game,
    start_game,
    get_current_player,
    validate_word,
    timeout_current_player,
    has_winner,
    reward_valid_word,
    reward_final,
    join_button,
)
from yumeko.games.bomb_party.strings import (
    lobby_text,
    join_countdown_text,
    joined_text,
    not_enough_text,
    turn_text,
    valid_word_text,
    timeout_text,
    eliminated_text,
    winner_text,
    invalid_word_text,
)
from yumeko.helpers.permissions import is_admin, is_bot_admin
from yumeko.locales import get_text


async def bomb_cmd(client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        await message.reply_text("Bomb Party can only be played in groups.")
        return

    chat_id = message.chat.id
    user = message.from_user

    if not user:
        return

    if not await is_admin(client, chat_id, user.id):
        await message.reply_text("Only group admins can start Bomb Party.")
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

    create_game(chat_id, user.id, user.first_name or "Unknown")
    lock_game(chat_id, "Bomb Party")

    game = get_game(chat_id)
    join_game(chat_id, user)

    game_started("Bomb Party", chat_id)

    await message.reply_text(
        lobby_text(game),
        parse_mode=ParseMode.HTML,
        reply_markup=join_button(),
        disable_web_page_preview=True,
    )

    asyncio.create_task(join_countdown(client, chat_id))


async def join_cmd(client, message: Message):
    chat_id = message.chat.id
    user = message.from_user

    if not user:
        return

    game = get_game(chat_id)

    if not game or game["status"] != "joining":
        return

    await add_user(user)

    ok, reason = join_game(chat_id, user)

    if not ok:
        if reason == "already_joined":
            await message.reply_text("You're already in, darling~", reply_to_message_id=message.id)
        elif reason == "full":
            await message.reply_text("The table is full, darling~", reply_to_message_id=message.id)
        return

    await message.reply_text(
        joined_text(user.first_name or "Unknown", len(game["players"])),
        parse_mode=ParseMode.HTML,
        reply_to_message_id=message.id,
    )


async def bomb_join_callback(client, query: CallbackQuery):
    chat_id = query.message.chat.id
    user = query.from_user

    game = get_game(chat_id)

    if not game or game["status"] != "joining":
        await query.answer("No open Bomb Party lobby, darling~", show_alert=True)
        return

    await add_user(user)

    ok, reason = join_game(chat_id, user)

    if not ok:
        if reason == "already_joined":
            await query.answer("You're already in, darling~", show_alert=True)
        elif reason == "full":
            await query.answer("The table is full, darling~", show_alert=True)
        else:
            await query.answer("You cannot join now.", show_alert=True)
        return

    await query.answer("You joined Bomb Party!")

    await query.message.reply_text(
        joined_text(user.first_name or "Unknown", len(game["players"])),
        parse_mode=ParseMode.HTML,
    )


async def join_countdown(client, chat_id: int):
    await asyncio.sleep(15)

    game = get_game(chat_id)

    if not game or game["status"] != "joining":
        return

    await client.send_message(
        chat_id,
        join_countdown_text(15),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

    await asyncio.sleep(15)

    game = get_game(chat_id)

    if not game or game["status"] != "joining":
        return

    if len(game["players"]) < MIN_PLAYERS:
        await client.send_message(
            chat_id,
            not_enough_text(game),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
        end_game(chat_id)
        unlock_game(chat_id)
        return

    start_game(chat_id)
    await send_turn(client, chat_id)


async def send_turn(client, chat_id: int):
    game = get_game(chat_id)

    if not game or game["status"] != "running":
        return

    player = get_current_player(chat_id)

    if not player:
        return

    token = game["turn_token"]

    await client.send_message(
        chat_id,
        turn_text(game, player),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

    asyncio.create_task(turn_timeout(client, chat_id, token))


async def turn_timeout(client, chat_id: int, token: int):
    await asyncio.sleep(TURN_TIME)

    game = get_game(chat_id)

    if not game or game["status"] != "running":
        return

    player, status = timeout_current_player(chat_id, token)

    if status == "old_turn":
        return

    if not player:
        return

    if status == "eliminated":
        await client.send_message(
            chat_id,
            eliminated_text(game, player),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
    else:
        await client.send_message(
            chat_id,
            timeout_text(game, player),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )

    winner = has_winner(chat_id)

    if winner:
        await reward_final(chat_id, winner["id"])

        await client.send_message(
            chat_id,
            winner_text(game, winner),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )

        game_finished("Bomb Party", winner["name"])
        end_game(chat_id)
        unlock_game(chat_id)
        return

    await send_turn(client, chat_id)


async def bomb_word_checker(client, message: Message):
    chat_id = message.chat.id
    user = message.from_user

    if not user or not message.text:
        return

    if message.text.startswith("/"):
        return

    game = get_game(chat_id)

    if not game or game["status"] != "running":
        return

    current_player = get_current_player(chat_id)

    if not current_player:
        return

    if current_player["id"] != user.id:
        return

    word = clean_word(message.text)

    if not word:
        await message.reply_text(
            "❌ Send a real word, darling~",
            reply_to_message_id=message.id,
        )
        return

    if not is_valid_dictionary_word(word):
        await message.reply_text(
            "❌ Invalid word.\n\nThat word doesn't exist in Yumeko's dictionary, darling~",
            reply_to_message_id=message.id,
        )
        return

    ok, result = validate_word(chat_id, user.id, word)

    if not ok:
        await message.reply_text(
            invalid_word_text(result, game),
            parse_mode=ParseMode.HTML,
            reply_to_message_id=message.id,
        )
        return

    await reward_valid_word(user.id)

    winner = has_winner(chat_id)

    if winner:
        await reward_final(chat_id, winner["id"])

        await message.reply_text(
            winner_text(game, winner),
            parse_mode=ParseMode.HTML,
            reply_to_message_id=message.id,
            disable_web_page_preview=True,
        )

        game_finished("Bomb Party", winner["name"])
        end_game(chat_id)
        unlock_game(chat_id)
        return

    player = get_current_player(chat_id)

    await message.reply_text(
        valid_word_text(game, player, result, user.first_name or "Unknown"),
        parse_mode=ParseMode.HTML,
        reply_to_message_id=message.id,
        disable_web_page_preview=True,
    )

    asyncio.create_task(turn_timeout(client, chat_id, game["turn_token"]))


def register_bomb_party_handlers(app):
    app.add_handler(
        MessageHandler(bomb_cmd, filters.command(["bombparty", "bomb"])),
        group=40,
    )

    app.add_handler(
        MessageHandler(join_cmd, filters.command("join") & filters.group),
        group=40,
    )

    app.add_handler(
        CallbackQueryHandler(bomb_join_callback, filters.regex("^bomb_join$")),
        group=40,
    )

    app.add_handler(
        MessageHandler(bomb_word_checker, filters.text & filters.group),
        group=-30,
    )