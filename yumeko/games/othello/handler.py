# ==========================================================
#  Yumeko Games Bot — Othello / Reversi Handler
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

from yumeko.database.users import add_user, add_win, add_loss, add_xp
from yumeko.database.groups import add_group

from yumeko.games.othello import strings as S
from yumeko.games.othello.game import (
    create_game,
    get_game,
    end_game,
    join_game,
    start_game,
    place_piece,
    current_player,
    format_players,
    board_text,
    final_scoreboard,
    count_pieces,
    BOARD_SIZE,
    MIN_PLAYERS,
    MAX_PLAYERS,
    WIN_COINS,
    WIN_XP,
    LOSE_XP,
    DRAW_XP,
)


def lobby_buttons():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🎮 Join Match", callback_data="ot_join")],
            [
                InlineKeyboardButton("▶️ Start", callback_data="ot_start"),
                InlineKeyboardButton("🛑 Cancel", callback_data="ot_cancel"),
            ],
        ]
    )


def board_buttons(game):
    rows = []

    for r in range(BOARD_SIZE):
        row = []

        for c in range(BOARD_SIZE):
            cell = game["board"][r][c]

            text = cell if cell else "·"

            row.append(
                InlineKeyboardButton(
                    text,
                    callback_data=f"ot_place_{r}_{c}",
                )
            )

        rows.append(row)

    rows.append([InlineKeyboardButton("🛑 End Match", callback_data="ot_end")])
    return InlineKeyboardMarkup(rows)


def arena_caption(game):
    current = current_player(game)
    counts = count_pieces(game)

    return S.arena_text(
        current["name"],
        current["piece"],
        board_text(game),
        counts["⚫"],
        counts["⚪"],
    )


async def cmd_othello(client: Client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        await message.reply_text("♟ Othello can only be played in groups.")
        return

    if not message.from_user:
        return

    await add_user(message.from_user)
    await add_group(message.chat)

    chat_id = message.chat.id

    if get_game(chat_id):
        await message.reply_text(
            S.ALREADY_RUNNING,
            parse_mode=ParseMode.HTML,
        )
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


async def cmd_othello_rules(client: Client, message: Message):
    await message.reply_text(
        S.rules_text(),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


async def cmd_end_othello(client: Client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        return

    if not message.from_user:
        return

    chat_id = message.chat.id
    game = get_game(chat_id)

    if not game:
        await message.reply_text(
            S.NO_GAME,
            parse_mode=ParseMode.HTML,
        )
        return

    if message.from_user.id not in game["players"] and message.from_user.id != game["host_id"]:
        await message.reply_text("Only players can end this Othello match.")
        return

    end_game(chat_id)

    await message.reply_text(
        "<blockquote>🛑 <b>Othello Ended</b></blockquote>\n\n"
        "<i>❝ Yumeko clears the black and white board~ ♡ ❞</i>",
        parse_mode=ParseMode.HTML,
    )


async def cb_join(client: Client, callback: CallbackQuery):
    if not callback.message:
        return

    await add_user(callback.from_user)

    chat_id = callback.message.chat.id
    user = callback.from_user
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

    await callback.answer("Othello started~ ♡")

    await callback.message.edit_text(
        arena_caption(game),
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


async def finish_game(callback: CallbackQuery, game, winner_id, draw=False):
    counts = count_pieces(game)

    if draw or not winner_id:
        for uid in game["players"]:
            await add_xp(uid, DRAW_XP)

        await callback.message.edit_text(
            S.draw_text(
                final_scoreboard(game),
                counts["⚫"],
                counts["⚪"],
            ),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )

        end_game(callback.message.chat.id)
        return

    winner = game["players"][winner_id]

    await add_win(winner_id, coins=WIN_COINS, xp=WIN_XP)

    for uid in game["players"]:
        if uid != winner_id:
            await add_loss(uid, xp=LOSE_XP)

    await callback.message.edit_text(
        S.winner_text(
            winner["name"],
            winner["piece"],
            final_scoreboard(game),
            counts["⚫"],
            counts["⚪"],
            WIN_COINS,
            WIN_XP,
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

    ok, reason, result = place_piece(chat_id, user.id, row, col)

    if not ok:
        msgs = {
            "not_turn": S.NOT_YOUR_TURN,
            "invalid_move": S.INVALID_MOVE,
            "not_player": S.NOT_PLAYER,
            "not_playing": "Match has not started.",
        }
        await callback.answer(msgs.get(reason, "Cannot place piece."), show_alert=True)
        return

    game = get_game(chat_id)
    player = result["player"]

    await callback.answer(f"Flipped {result['flips']} pieces~ ♡")

    if result["game_over"]:
        await finish_game(callback, game, result["winner"], result["draw"])
        return

    prefix = S.move_text(
        player["name"],
        player["piece"],
        row,
        col,
        result["flips"],
    )

    if result["skipped"]:
        prefix += "\n\n" + S.skip_turn_text(result["skipped"]["name"])

    await callback.message.edit_text(
        prefix + "\n\n" + arena_caption(game),
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
        "<blockquote>🛑 <b>Othello Ended</b></blockquote>\n\n"
        "<i>❝ The board returns to stillness~ ♡ ❞</i>",
        parse_mode=ParseMode.HTML,
    )


def register_othello_handlers(app: Client):
    app.add_handler(
        MessageHandler(
            cmd_othello,
            filters.command(["othello", "reversi"]) & filters.group,
        ),
        group=530,
    )

    app.add_handler(
        MessageHandler(
            cmd_end_othello,
            filters.command(["endothello", "stopothello", "endreversi"]) & filters.group,
        ),
        group=530,
    )

    app.add_handler(
        MessageHandler(
            cmd_othello_rules,
            filters.command(["othellorules", "reversirules"]) & filters.group,
        ),
        group=530,
    )

    app.add_handler(CallbackQueryHandler(cb_join, filters.regex("^ot_join$")), group=530)
    app.add_handler(CallbackQueryHandler(cb_start, filters.regex("^ot_start$")), group=530)
    app.add_handler(CallbackQueryHandler(cb_cancel, filters.regex("^ot_cancel$")), group=530)
    app.add_handler(CallbackQueryHandler(cb_place, filters.regex(r"^ot_place_\d+_\d+$")), group=530)
    app.add_handler(CallbackQueryHandler(cb_end, filters.regex("^ot_end$")), group=530)