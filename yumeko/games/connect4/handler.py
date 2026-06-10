# ==========================================================
#  Yumeko Games Bot — Connect Four Handler
#  Copyright (c) 2026 Jass
# ==========================================================

import asyncio

from pyrogram import Client, filters
from pyrogram.enums import ChatType, ParseMode
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.types import Message, CallbackQuery

from yumeko.core.game_manager import is_game_running, get_running_game, lock_game, unlock_game
from yumeko.database.users import add_user, add_win, add_loss
from yumeko.database.groups import add_group

from yumeko.games.connect4.game import (
    create_game,
    get_game,
    end_game,
    join_game,
    start_game,
    drop_piece,
    format_board,
    players_text,
    current_player,
    WIN_COINS,
    WIN_XP,
    LOSE_XP,
)

from yumeko.games.connect4.buttons import (
    join_buttons,
    column_buttons,
    after_game_buttons,
)

from yumeko.games.connect4 import strings as S


JOIN_TIMEOUT = 45


async def cmd_connect4(client: Client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        await message.reply_text("🔴🟡 Connect Four can only be played in groups.")
        return

    if not message.from_user:
        return

    chat_id = message.chat.id
    user = message.from_user

    await add_user(user)
    await add_group(message.chat)

    if is_game_running(chat_id):
        await message.reply_text(
            f"<b>{get_running_game(chat_id)}</b> is already running!",
            parse_mode=ParseMode.HTML,
        )
        return

    if get_game(chat_id):
        await message.reply_text(S.ALREADY_RUNNING)
        return

    game = create_game(chat_id, user)
    lock_game(chat_id, "Connect Four")

    msg = await message.reply_text(
        S.lobby_text(
            user.first_name or "Unknown",
            players_text(game),
            len(game["players"]),
            JOIN_TIMEOUT,
        ),
        reply_markup=join_buttons(),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

    asyncio.create_task(auto_start(client, msg, chat_id))


async def auto_start(client: Client, message: Message, chat_id: int):
    await asyncio.sleep(JOIN_TIMEOUT)

    game = get_game(chat_id)

    if not game or game["status"] != "joining":
        return

    if len(game["players"]) < 2:
        end_game(chat_id)
        unlock_game(chat_id)

        await message.edit_text(
            S.NOT_ENOUGH,
            parse_mode=ParseMode.HTML,
        )
        return

    await launch_game(client, message, chat_id)


async def launch_game(client: Client, message, chat_id: int):
    ok, reason = start_game(chat_id)

    if not ok:
        await message.edit_text(
            S.NOT_ENOUGH,
            parse_mode=ParseMode.HTML,
        )
        return

    game = get_game(chat_id)
    player = current_player(game)

    await message.edit_text(
        S.game_started_text(players_text(game))
        + "\n\n"
        + f"<pre>{format_board(game)}</pre>\n\n"
        + S.turn_text(player["name"], player["piece"]),
        reply_markup=column_buttons(),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


async def cb_c4_join(client: Client, callback: CallbackQuery):
    if not callback.message:
        return

    chat_id = callback.message.chat.id
    user = callback.from_user

    await add_user(user)

    game = get_game(chat_id)

    if not game:
        await callback.answer("❌ No active Connect Four lobby.", show_alert=True)
        return

    ok, reason = join_game(chat_id, user)

    if not ok:
        msgs = {
            "started": "⚡ Match already started.",
            "full": S.GAME_FULL,
            "joined": S.ALREADY_JOINED,
        }
        await callback.answer(msgs.get(reason, "❌ Cannot join."), show_alert=True)
        return

    await callback.answer("🔴🟡 Joined Connect Four!", show_alert=False)

    game = get_game(chat_id)
    host_name = game["players"][game["host_id"]]["name"]

    await callback.message.edit_text(
        S.lobby_text(
            host_name,
            players_text(game),
            len(game["players"]),
            JOIN_TIMEOUT,
        ),
        reply_markup=join_buttons(),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


async def cb_c4_start(client: Client, callback: CallbackQuery):
    if not callback.message:
        return

    chat_id = callback.message.chat.id
    user = callback.from_user
    game = get_game(chat_id)

    if not game:
        await callback.answer("❌ No active lobby.", show_alert=True)
        return

    if user.id != game["host_id"]:
        await callback.answer(S.HOST_ONLY, show_alert=True)
        return

    if len(game["players"]) < 2:
        await callback.answer(S.NOT_ENOUGH, show_alert=True)
        return

    await callback.answer("Starting Connect Four~ ♡", show_alert=False)
    await launch_game(client, callback.message, chat_id)


async def cb_c4_cancel(client: Client, callback: CallbackQuery):
    if not callback.message:
        return

    chat_id = callback.message.chat.id
    user = callback.from_user
    game = get_game(chat_id)

    if not game:
        await callback.answer("❌ No match.", show_alert=True)
        return

    if user.id != game["host_id"]:
        await callback.answer(S.HOST_ONLY, show_alert=True)
        return

    end_game(chat_id)
    unlock_game(chat_id)

    await callback.answer("Cancelled.", show_alert=False)

    await callback.message.edit_text(
        S.GAME_CANCELLED,
        parse_mode=ParseMode.HTML,
    )


async def cb_c4_col(client: Client, callback: CallbackQuery):
    if not callback.message:
        return

    chat_id = callback.message.chat.id
    user = callback.from_user
    game = get_game(chat_id)

    if not game:
        await callback.answer("❌ No active match.", show_alert=True)
        return

    try:
        col = int(callback.data.replace("c4_col_", "", 1))
    except Exception:
        await callback.answer("Invalid column.", show_alert=True)
        return

    ok, reason, result = drop_piece(chat_id, user.id, col)

    if not ok:
        if reason == "not_turn":
            await callback.answer(S.NOT_YOUR_TURN, show_alert=True)
        elif reason == "column_full":
            await callback.answer(S.COLUMN_FULL, show_alert=True)
        else:
            await callback.answer("Cannot move there.", show_alert=True)
        return

    game = get_game(chat_id)

    await callback.answer("Piece dropped.", show_alert=False)

    if reason == "winner":
        winner = result["player"]

        for uid in game["players"]:
            if uid == winner["id"]:
                await add_win(uid, coins=WIN_COINS, xp=WIN_XP)
            else:
                await add_loss(uid, xp=LOSE_XP)

        reward_text = (
            "\n\n"
            "<blockquote>🎁 <b>Victory Rewards</b></blockquote>\n\n"
            f"🪙 Coins: +<b>{WIN_COINS}</b>\n"
            f"⭐ XP: +<b>{WIN_XP}</b>\n"
            f"🏆 Win Added: +<b>1</b>\n\n"
            f"📉 Other Player: +<b>{LOSE_XP}</b> XP\n\n"
            "<i>❝ Yumeko smiles upon today's winner~ ♡ ❞</i>"
        )

        await callback.message.edit_text(
            f"<pre>{format_board(game)}</pre>\n\n"
            + S.winner_text(winner["name"], winner["piece"])
            + reward_text,
            reply_markup=after_game_buttons(),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )

        end_game(chat_id)
        unlock_game(chat_id)
        return

    if reason == "draw":
        await callback.message.edit_text(
            f"<pre>{format_board(game)}</pre>\n\n"
            + S.DRAW_GAME,
            reply_markup=after_game_buttons(),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )

        end_game(chat_id)
        unlock_game(chat_id)
        return

    player = current_player(game)

    await callback.message.edit_text(
        S.move_text(result["player"]["name"], result["piece"], col + 1)
        + "\n\n"
        + f"<pre>{format_board(game)}</pre>\n\n"
        + S.turn_text(player["name"], player["piece"]),
        reply_markup=column_buttons(),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


async def cb_c4_end(client: Client, callback: CallbackQuery):
    if not callback.message:
        return

    chat_id = callback.message.chat.id
    game = get_game(chat_id)

    if not game:
        await callback.answer("❌ No match.", show_alert=True)
        return

    user_id = callback.from_user.id

    if user_id != game["host_id"] and user_id not in game["players"]:
        await callback.answer("Only players can end this match.", show_alert=True)
        return

    end_game(chat_id)
    unlock_game(chat_id)

    await callback.answer("Match ended.", show_alert=False)

    await callback.message.edit_text(
        "<blockquote>🛑 <b>Connect Four Ended</b></blockquote>\n\n"
        "<i>❝ The board falls silent~ ♡ ❞</i>",
        parse_mode=ParseMode.HTML,
    )


async def cmd_endconnect4(client: Client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        return

    if not message.from_user:
        return

    chat_id = message.chat.id
    game = get_game(chat_id)

    if not game:
        await message.reply_text("No Connect Four match is running.")
        return

    user_id = message.from_user.id

    if user_id != game["host_id"] and user_id not in game["players"]:
        await message.reply_text("Only players can end this match.")
        return

    end_game(chat_id)
    unlock_game(chat_id)

    await message.reply_text(
        "<blockquote>🛑 <b>Connect Four Ended</b></blockquote>\n\n"
        "<i>❝ The board falls silent~ ♡ ❞</i>",
        parse_mode=ParseMode.HTML,
    )


async def cb_c4_play_again(client: Client, callback: CallbackQuery):
    await callback.answer("Use /connect4 to start again.")
    await callback.message.reply_text("Use /connect4 to start a new Connect Four match.")


def register_connect4_handlers(app: Client):
    app.add_handler(
        MessageHandler(
            cmd_connect4,
            filters.command(["connect4", "c4"]) & filters.group,
        ),
        group=380,
    )

    app.add_handler(
        MessageHandler(
            cmd_endconnect4,
            filters.command(["endconnect4", "stopconnect4", "endc4"]) & filters.group,
        ),
        group=380,
    )

    app.add_handler(
        CallbackQueryHandler(cb_c4_join, filters.regex("^c4_join$")),
        group=380,
    )

    app.add_handler(
        CallbackQueryHandler(cb_c4_start, filters.regex("^c4_start$")),
        group=380,
    )

    app.add_handler(
        CallbackQueryHandler(cb_c4_cancel, filters.regex("^c4_cancel$")),
        group=380,
    )

    app.add_handler(
        CallbackQueryHandler(cb_c4_col, filters.regex("^c4_col_")),
        group=380,
    )

    app.add_handler(
        CallbackQueryHandler(cb_c4_end, filters.regex("^c4_end$")),
        group=380,
    )

    app.add_handler(
        CallbackQueryHandler(cb_c4_play_again, filters.regex("^c4_play_again$")),
        group=380,
    )