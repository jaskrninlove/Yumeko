# ==========================================================
#  Yumeko Games Bot — Gomoku Handler
#  Copyright (c) 2026 Jass
# ==========================================================

from pyrogram import Client, filters
from pyrogram.enums import ChatType, ParseMode
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from yumeko.database.users import add_user, add_win, add_loss
from yumeko.database.groups import add_group

from yumeko.games.gomoku import strings as S
from yumeko.games.gomoku.game import (
    create_game,
    get_game,
    end_game,
    join_game,
    start_game,
    place_stone,
    current_player,
    format_players,
    board_text,
    final_scoreboard,
    BOARD_SIZE,
    MIN_PLAYERS,
    MAX_PLAYERS,
    WIN_COINS,
    WIN_XP,
    LOSE_XP,
)


def lobby_buttons():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🎮 Join Match", callback_data="gm_join")],
            [
                InlineKeyboardButton("▶️ Start", callback_data="gm_start"),
                InlineKeyboardButton("🛑 Cancel", callback_data="gm_cancel"),
            ],
        ]
    )


def board_buttons(game):
    rows = []

    for r in range(BOARD_SIZE):
        row = []

        for c in range(BOARD_SIZE):
            owner = game["board"][r][c]

            if owner is None:
                text = "·"
            else:
                text = game["players"][owner]["stone"]

            row.append(
                InlineKeyboardButton(
                    text,
                    callback_data=f"gm_place_{r}_{c}",
                )
            )

        rows.append(row)

    rows.append([InlineKeyboardButton("🛑 End Match", callback_data="gm_end")])
    return InlineKeyboardMarkup(rows)


async def cmd_gomoku(client: Client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        await message.reply_text("⚫ Gomoku can only be played in groups.")
        return

    if not message.from_user:
        return

    await add_user(message.from_user)
    await add_group(message.chat)

    chat_id = message.chat.id

    if get_game(chat_id):
        await message.reply_text(S.ALREADY_RUNNING)
        return

    game = create_game(chat_id, message.from_user)

    await message.reply_text(
        S.lobby_text(
            game["host_name"],
            format_players(game),
            len(game["players"]),
            MAX_PLAYERS,
        ),
        reply_markup=lobby_buttons(),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


async def cmd_gomoku_rules(client: Client, message: Message):
    await message.reply_text(
        S.rules_text(),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


async def cmd_end_gomoku(client: Client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        return

    if not message.from_user:
        return

    chat_id = message.chat.id
    game = get_game(chat_id)

    if not game:
        await message.reply_text(S.NO_GAME)
        return

    if message.from_user.id not in game["players"] and message.from_user.id != game["host_id"]:
        await message.reply_text("Only players can end this Gomoku match.")
        return

    end_game(chat_id)

    await message.reply_text(
        "<blockquote>🛑 <b>Gomoku Ended</b></blockquote>\n\n"
        "<i>❝ The stones return to silence~ ♡ ❞</i>",
        parse_mode=ParseMode.HTML,
    )


async def cb_join(client: Client, callback: CallbackQuery):
    if not callback.message:
        return

    chat_id = callback.message.chat.id
    user = callback.from_user

    await add_user(user)

    game = get_game(chat_id)

    if not game:
        await callback.answer(S.NO_GAME, show_alert=True)
        return

    ok, reason = join_game(chat_id, user)

    if not ok:
        msgs = {
            "started": "⚡ Match already started.",
            "joined": S.ALREADY_JOINED,
            "full": S.GAME_FULL,
        }
        await callback.answer(msgs.get(reason, "Cannot join."), show_alert=True)
        return

    await callback.answer("⚪ Joined the board~ ♡")

    game = get_game(chat_id)

    await callback.message.edit_text(
        S.lobby_text(
            game["host_name"],
            format_players(game),
            len(game["players"]),
            MAX_PLAYERS,
        ),
        reply_markup=lobby_buttons(),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


async def cb_start(client: Client, callback: CallbackQuery):
    if not callback.message:
        return

    chat_id = callback.message.chat.id
    game = get_game(chat_id)

    if not game:
        await callback.answer(S.NO_GAME, show_alert=True)
        return

    if callback.from_user.id != game["host_id"]:
        await callback.answer(S.HOST_ONLY, show_alert=True)
        return

    if len(game["players"]) < MIN_PLAYERS:
        await callback.answer(S.NOT_ENOUGH, show_alert=True)
        return

    ok, reason = start_game(chat_id)

    if not ok:
        await callback.answer(S.NOT_ENOUGH, show_alert=True)
        return

    game = get_game(chat_id)
    current = current_player(game)

    await callback.answer("Gomoku started~ ♡")

    await callback.message.edit_text(
        S.arena_text(
            board_text(game),
            current["name"],
            current["stone"],
        ),
        reply_markup=board_buttons(game),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


async def cb_cancel(client: Client, callback: CallbackQuery):
    if not callback.message:
        return

    chat_id = callback.message.chat.id
    game = get_game(chat_id)

    if not game:
        await callback.answer(S.NO_GAME, show_alert=True)
        return

    if callback.from_user.id != game["host_id"]:
        await callback.answer(S.HOST_ONLY, show_alert=True)
        return

    end_game(chat_id)

    await callback.answer("Cancelled.")
    await callback.message.edit_text(
        S.GAME_CANCELLED,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


async def finish_win(callback: CallbackQuery, game, winner_id):
    winner = game["players"][winner_id]

    await add_win(winner_id, coins=WIN_COINS, xp=WIN_XP)

    for uid in game["players"]:
        if uid != winner_id:
            await add_loss(uid, xp=LOSE_XP)

    await callback.message.edit_text(
        S.winner_text(
            winner["name"],
            winner["stone"],
            board_text(game),
            final_scoreboard(game),
            WIN_COINS,
            WIN_XP,
        ),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

    end_game(callback.message.chat.id)


async def finish_draw(callback: CallbackQuery, game):
    for uid in game["players"]:
        await add_loss(uid, xp=LOSE_XP)

    await callback.message.edit_text(
        S.draw_text(
            board_text(game),
            final_scoreboard(game),
        ),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

    end_game(callback.message.chat.id)


async def cb_place(client: Client, callback: CallbackQuery):
    if not callback.message:
        return

    chat_id = callback.message.chat.id
    user = callback.from_user
    game = get_game(chat_id)

    if not game:
        await callback.answer(S.NO_GAME, show_alert=True)
        return

    try:
        _, _, row, col = callback.data.split("_")
        row = int(row)
        col = int(col)
    except Exception:
        await callback.answer("Invalid move.", show_alert=True)
        return

    ok, reason, result = place_stone(chat_id, user.id, row, col)

    if not ok:
        msgs = {
            "not_turn": S.NOT_YOUR_TURN,
            "occupied": S.OCCUPIED,
            "not_player": S.NOT_PLAYER,
            "not_playing": "Match has not started.",
        }
        await callback.answer(msgs.get(reason, "Cannot place stone."), show_alert=True)
        return

    game = get_game(chat_id)
    player = result["player"]

    await callback.answer("Stone placed~ ♡")

    if result["won"]:
        await finish_win(callback, game, result["winner"])
        return

    if result["draw"]:
        await finish_draw(callback, game)
        return

    current = current_player(game)

    await callback.message.edit_text(
        S.move_text(
            player["name"],
            player["stone"],
            row,
            col,
        )
        + S.arena_text(
            board_text(game),
            current["name"],
            current["stone"],
        ),
        reply_markup=board_buttons(game),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


async def cb_end(client: Client, callback: CallbackQuery):
    if not callback.message:
        return

    chat_id = callback.message.chat.id
    game = get_game(chat_id)

    if not game:
        await callback.answer(S.NO_GAME, show_alert=True)
        return

    if callback.from_user.id not in game["players"] and callback.from_user.id != game["host_id"]:
        await callback.answer("Only players can end this.", show_alert=True)
        return

    end_game(chat_id)

    await callback.answer("Match ended.")
    await callback.message.edit_text(
        "<blockquote>🛑 <b>Gomoku Ended</b></blockquote>\n\n"
        "<i>❝ Yumeko clears the ancient board~ ♡ ❞</i>",
        parse_mode=ParseMode.HTML,
    )


def register_gomoku_handlers(app: Client):
    app.add_handler(
        MessageHandler(
            cmd_gomoku,
            filters.command(["gomoku", "fiveinarow"]) & filters.group,
        ),
        group=470,
    )

    app.add_handler(
        MessageHandler(
            cmd_end_gomoku,
            filters.command(["endgomoku", "stopgomoku"]) & filters.group,
        ),
        group=470,
    )

    app.add_handler(
        MessageHandler(
            cmd_gomoku_rules,
            filters.command(["gomokurules", "fiveinarowrules"]) & filters.group,
        ),
        group=470,
    )

    app.add_handler(CallbackQueryHandler(cb_join, filters.regex("^gm_join$")), group=470)
    app.add_handler(CallbackQueryHandler(cb_start, filters.regex("^gm_start$")), group=470)
    app.add_handler(CallbackQueryHandler(cb_cancel, filters.regex("^gm_cancel$")), group=470)
    app.add_handler(CallbackQueryHandler(cb_place, filters.regex(r"^gm_place_\d+_\d+$")), group=470)
    app.add_handler(CallbackQueryHandler(cb_end, filters.regex("^gm_end$")), group=470)