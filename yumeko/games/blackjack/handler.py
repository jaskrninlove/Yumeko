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
from yumeko.games.blackjack.game import (
    JOIN_TIME,
    MIN_PLAYERS,
    create_game,
    get_game,
    end_game,
    join_game,
    start_game,
    get_current_player,
    hit,
    stand,
    surrender,
    all_players_done,
    dealer_play,
    reward_results,
    join_button,
    action_buttons,
)
from yumeko.games.blackjack.strings import (
    lobby_text,
    joined_text,
    countdown_text,
    not_enough_text,
    turn_text,
    blackjack_auto_text,
    hit_text,
    bust_text,
    stand_text,
    surrender_text,
    final_text,
    rules_text,
    stopped_text,
)
from yumeko.games.mafia.game import add_afk_warning, check_winner, get_non_voters, kill_lover_if_needed, kill_player
from yumeko.games.number_bomb.game import finish_game
from yumeko.helpers.permissions import is_admin, is_bot_admin
from yumeko.locales import get_text


async def bj_cmd(client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        await message.reply_text("Blackjack can only be played in groups.")
        return

    chat_id = message.chat.id
    user = message.from_user

    if not user:
        return

    if not await is_admin(client, chat_id, user.id):
        await message.reply_text("Only group admins can open a Blackjack table.")
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
    lock_game(chat_id, "Blackjack")

    game = get_game(chat_id)
    join_game(chat_id, user)

    game_started("Blackjack", chat_id)

    await message.reply_text(
        lobby_text(game),
        parse_mode=ParseMode.HTML,
        reply_markup=join_button(),
        disable_web_page_preview=True,
    )

    asyncio.create_task(join_countdown(client, chat_id))


async def bj_rules_cmd(client, message: Message):
    await message.reply_text(
        rules_text(),
        parse_mode=ParseMode.HTML,
        reply_to_message_id=message.id,
        disable_web_page_preview=True,
    )


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
            await message.reply_text("You're already seated, darling~", reply_to_message_id=message.id)
        elif reason == "full":
            await message.reply_text("The table is full, darling~", reply_to_message_id=message.id)
        elif reason == "dead_player":
            await message.reply_text("Dead players cannot rejoin this match.")
        return

    await message.reply_text(
        joined_text(user.first_name or "Unknown", len(game["players"])),
        parse_mode=ParseMode.HTML,
        reply_to_message_id=message.id,
    )

async def apply_vote_afk(client, chat_id: int):
    game = get_game(chat_id)

    if not game:
        return

    non_voters = get_non_voters(game)

    for uid in non_voters:
        warnings = add_afk_warning(game, uid)
        player = game["players"].get(uid)

        if not player:
            continue

        if warnings >= 2 and uid in game["alive"]:
            killed = kill_player(game, uid)
            if killed:
                kill_lover_if_needed(game,uid)

            winner = check_winner(chat_id)

            if winner:
                await finish_game(client, chat_id, winner)
                return
            if killed:
                await client.send_message(
                    chat_id,
                    (
                        "<blockquote>⚠️ <b>AFK Removal</b></blockquote>\n\n"
                        f"<b>{player['name']}</b> was removed for inactivity.\n\n"
                        "<i>They missed too many votes.</i>"
                    ),
                    parse_mode=ParseMode.HTML,
                )
        else:
            try:
                await client.send_message(
                    uid,
                    (
                        "<blockquote>⚠️ <b>AFK Warning</b></blockquote>\n\n"
                        "You missed the village vote.\n"
                        f"Warning: <b>{warnings}/2</b>\n\n"
                        "<i>Miss another vote and Yumeko may remove you from the table.</i>"
                    ),
                    parse_mode=ParseMode.HTML,
                )
            except Exception:
                pass

async def bj_join_callback(client, query: CallbackQuery):
    chat_id = query.message.chat.id
    user = query.from_user

    game = get_game(chat_id)

    if not game or game["status"] != "joining":
        await query.answer("No open Blackjack table, darling~", show_alert=True)
        return

    await add_user(user)

    ok, reason = join_game(chat_id, user)

    if not ok:
        if reason == "already_joined":
            await query.answer("You're already seated, darling~", show_alert=True)
        elif reason == "full":
            await query.answer("The table is full, darling~", show_alert=True)
        else:
            await query.answer("You cannot join now.", show_alert=True)
        return

    await query.answer("You joined Blackjack!")

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
        countdown_text(15),
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

    auto = blackjack_auto_text(game)
    player = get_current_player(chat_id)

    if auto:
        await client.send_message(chat_id, auto, parse_mode=ParseMode.HTML)

    if not player:
        await finish_blackjack(client, chat_id)
        return

    await send_turn(client, chat_id)


async def send_turn(client, chat_id: int):
    game = get_game(chat_id)

    if not game or game["status"] != "running":
        return

    player = get_current_player(chat_id)

    if not player:
        await finish_blackjack(client, chat_id)
        return

    await client.send_message(
        chat_id,
        turn_text(game, player),
        parse_mode=ParseMode.HTML,
        reply_markup=action_buttons(),
        disable_web_page_preview=True,
    )


async def bj_hit(client, query: CallbackQuery):
    chat_id = query.message.chat.id
    user = query.from_user

    game = get_game(chat_id)

    if not game or game["status"] != "running":
        await query.answer("No active Blackjack round.", show_alert=True)
        return

    ok, result = hit(chat_id, user.id)

    if not ok:
        await query.answer("Not your turn, darling~", show_alert=True)
        return

    player = game["players"][user.id]

    if result == "bust":
        await query.message.edit_text(
            bust_text(player),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
    else:
        await query.message.edit_text(
            hit_text(player),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )

    await query.answer("Card drawn.")

    if all_players_done(chat_id):
        await finish_blackjack(client, chat_id)
    else:
        await send_turn(client, chat_id)


async def bj_stand(client, query: CallbackQuery):
    chat_id = query.message.chat.id
    user = query.from_user

    game = get_game(chat_id)

    if not game or game["status"] != "running":
        await query.answer("No active Blackjack round.", show_alert=True)
        return

    ok, result = stand(chat_id, user.id)

    if not ok:
        await query.answer("Not your turn, darling~", show_alert=True)
        return

    player = game["players"][user.id]

    await query.message.edit_text(
        stand_text(player),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

    await query.answer("Stand.")

    if all_players_done(chat_id):
        await finish_blackjack(client, chat_id)
    else:
        await send_turn(client, chat_id)


async def bj_surrender(client, query: CallbackQuery):
    chat_id = query.message.chat.id
    user = query.from_user

    game = get_game(chat_id)

    if not game or game["status"] != "running":
        await query.answer("No active Blackjack round.", show_alert=True)
        return

    ok, result = surrender(chat_id, user.id)

    if not ok:
        await query.answer("Not your turn, darling~", show_alert=True)
        return

    player = game["players"][user.id]

    await query.message.edit_text(
        surrender_text(player),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

    await query.answer("Surrendered.")

    if all_players_done(chat_id):
        await finish_blackjack(client, chat_id)
    else:
        await send_turn(client, chat_id)


async def finish_blackjack(client, chat_id: int):
    game = get_game(chat_id)

    if not game:
        return

    dealer_play(chat_id)
    await reward_results(chat_id)

    await client.send_message(
        chat_id,
        final_text(game),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

    game_finished("Blackjack", "Completed")
    end_game(chat_id)
    unlock_game(chat_id)


def register_blackjack_handlers(app):
    app.add_handler(
        MessageHandler(bj_cmd, filters.command(["blackjack", "bj"])),
        group=110,
    )

    app.add_handler(
        MessageHandler(bj_rules_cmd, filters.command(["blackjackrules", "bjrules", "bjhelp"])),
        group=110,
    )

    app.add_handler(
        MessageHandler(join_cmd, filters.command("join") & filters.group),
        group=110,
    )

    app.add_handler(
        CallbackQueryHandler(bj_join_callback, filters.regex("^bj_join$")),
        group=110,
    )

    app.add_handler(
        CallbackQueryHandler(bj_hit, filters.regex("^bj_hit$")),
        group=110,
    )

    app.add_handler(
        CallbackQueryHandler(bj_stand, filters.regex("^bj_stand$")),
        group=110,
    )

    app.add_handler(
        CallbackQueryHandler(bj_surrender, filters.regex("^bj_surrender$")),
        group=110,
    )