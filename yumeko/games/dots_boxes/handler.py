# ==========================================================
#  Yumeko Games Bot — Dots & Boxes Handler
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
from yumeko.games.dots_boxes import strings as S
from yumeko.games.dots_boxes.game import (
    create_game,
    get_game,
    end_game,
    join_game,
    start_game,
    draw_line,
    current_player,
    format_players,
    board_text,
    final_scoreboard,
    MIN_PLAYERS,
    MAX_PLAYERS,
    GRID_SIZE,
    BOX_SIZE,
    WIN_COINS,
    WIN_XP,
    LOSE_XP,
    DRAW_XP,
)


def lobby_buttons():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🎮 Join Game", callback_data="db_join")],
            [
                InlineKeyboardButton("▶️ Start", callback_data="db_start"),
                InlineKeyboardButton("🛑 Cancel", callback_data="db_cancel"),
            ],
        ]
    )


def board_buttons(game):
    rows = []

    for r in range(GRID_SIZE):
        row = []

        for c in range(BOX_SIZE):
            drawn = game["h_lines"][r][c]

            row.append(
                InlineKeyboardButton(
                    "━━" if drawn else "─",
                    callback_data="db_noop" if drawn else f"dbh_{r}_{c}",
                )
            )

        rows.append(row)

    for r in range(BOX_SIZE):
        row = []

        for c in range(GRID_SIZE):
            drawn = game["v_lines"][r][c]

            row.append(
                InlineKeyboardButton(
                    "┃" if drawn else "│",
                    callback_data="db_noop" if drawn else f"dbv_{r}_{c}",
                )
            )

        rows.append(row)

    rows.append([InlineKeyboardButton("🛑 End Match", callback_data="db_end")])
    return InlineKeyboardMarkup(rows)


def arena_caption(game):
    player = current_player(game)

    if not player:
        return "<i>No current player.</i>"

    return S.arena_text(
        board_text(game),
        player["name"],
        player["mark"],
        game["round"],
    )


async def cmd_dots(client: Client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        await message.reply_text("▪️ Dots & Boxes can only be played in groups.")
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
        parse_mode=ParseMode.HTML,
        reply_markup=lobby_buttons(),
        disable_web_page_preview=True,
    )


async def cmd_rules(client: Client, message: Message):
    await message.reply_text(
        S.rules_text(),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


async def cmd_end(client: Client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        return

    if not message.from_user:
        return

    chat_id = message.chat.id
    game = get_game(chat_id)

    if not game:
        await message.reply_text(S.NO_GAME)
        return

    if (
        message.from_user.id not in game["players"]
        and message.from_user.id != game["host_id"]
    ):
        await message.reply_text("Only players can end this Dots & Boxes game.")
        return

    end_game(chat_id)

    await message.reply_text(
        "<blockquote>🛑 <b>Dots & Boxes Ended</b></blockquote>\n\n"
        "<i>❝ The dots return to silence~ ♡ ❞</i>",
        parse_mode=ParseMode.HTML,
    )


async def cb_join(client: Client, callback: CallbackQuery):
    if not callback.message:
        return

    await add_user(callback.from_user)

    chat_id = callback.message.chat.id
    game = get_game(chat_id)

    if not game:
        await callback.answer(S.NO_GAME, show_alert=True)
        return

    ok, reason = join_game(chat_id, callback.from_user)

    if not ok:
        mapping = {
            "joined": S.ALREADY_JOINED,
            "full": S.GAME_FULL,
            "started": "⚡ Game already started.",
        }

        await callback.answer(mapping.get(reason, "Cannot join."), show_alert=True)
        return

    game = get_game(chat_id)

    await callback.message.edit_text(
        S.lobby_text(
            game["host_name"],
            format_players(game),
            len(game["players"]),
            MAX_PLAYERS,
        ),
        parse_mode=ParseMode.HTML,
        reply_markup=lobby_buttons(),
        disable_web_page_preview=True,
    )

    await callback.answer("Joined~ ♡")


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

    await callback.message.edit_text(
        arena_caption(game),
        parse_mode=ParseMode.HTML,
        reply_markup=board_buttons(game),
        disable_web_page_preview=True,
    )

    await callback.answer("Game started~ ♡")


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

    await callback.message.edit_text(
        S.GAME_CANCELLED,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

    await callback.answer("Cancelled.")


async def finish_game(callback: CallbackQuery, game, result):
    if result["draw"]:
        for uid in game["players"]:
            await add_xp(uid, DRAW_XP)

        await callback.message.edit_text(
            S.draw_text(
                final_scoreboard(game),
                DRAW_XP,
            ),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )

        end_game(callback.message.chat.id)
        return

    winner_id = result["winner"]
    winner = game["players"][winner_id]

    await add_win(winner_id, coins=WIN_COINS, xp=WIN_XP)

    for uid in game["players"]:
        if uid != winner_id:
            await add_loss(uid, xp=LOSE_XP)

    await callback.message.edit_text(
        S.winner_text(
            winner["name"],
            winner["mark"],
            final_scoreboard(game),
            WIN_COINS,
            WIN_XP,
        ),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

    end_game(callback.message.chat.id)


async def process_move(callback: CallbackQuery, line_type: str, row: int, col: int):
    if not callback.message:
        return

    chat_id = callback.message.chat.id
    game = get_game(chat_id)

    if not game:
        await callback.answer(S.NO_GAME, show_alert=True)
        return

    ok, reason, result = draw_line(
        chat_id,
        callback.from_user.id,
        line_type,
        row,
        col,
    )

    if not ok:
        mapping = {
            "not_turn": S.NOT_YOUR_TURN,
            "not_player": S.NOT_PLAYER,
            "invalid_line": S.INVALID_LINE,
            "not_playing": "Game has not started.",
        }

        await callback.answer(mapping.get(reason, "Cannot draw line."), show_alert=True)
        return

    game = get_game(chat_id)

    await callback.answer(
        "Box claimed! Extra turn~ ♡"
        if result["completed"]
        else "Line drawn~ ♡"
    )

    if result["game_over"]:
        await finish_game(callback, game, result)
        return

    move_text = S.move_text(
        result["player"]["name"],
        result["player"]["mark"],
        line_type,
        row,
        col,
        result["completed"],
    )

    await callback.message.edit_text(
        move_text + "\n\n" + arena_caption(game),
        parse_mode=ParseMode.HTML,
        reply_markup=board_buttons(game),
        disable_web_page_preview=True,
    )


async def cb_h(client: Client, callback: CallbackQuery):
    try:
        _, row, col = callback.data.split("_")
        row = int(row)
        col = int(col)
    except Exception:
        await callback.answer("Invalid line.", show_alert=True)
        return

    await process_move(callback, "h", row, col)


async def cb_v(client: Client, callback: CallbackQuery):
    try:
        _, row, col = callback.data.split("_")
        row = int(row)
        col = int(col)
    except Exception:
        await callback.answer("Invalid line.", show_alert=True)
        return

    await process_move(callback, "v", row, col)


async def cb_end(client: Client, callback: CallbackQuery):
    if not callback.message:
        return

    chat_id = callback.message.chat.id
    game = get_game(chat_id)

    if not game:
        await callback.answer(S.NO_GAME, show_alert=True)
        return

    if (
        callback.from_user.id not in game["players"]
        and callback.from_user.id != game["host_id"]
    ):
        await callback.answer("Only players can end this.", show_alert=True)
        return

    end_game(chat_id)

    await callback.message.edit_text(
        "<blockquote>🛑 <b>Dots & Boxes Ended</b></blockquote>\n\n"
        "<i>❝ Yumeko clears the little board~ ♡ ❞</i>",
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

    await callback.answer("Game ended.")


async def cb_noop(client: Client, callback: CallbackQuery):
    await callback.answer("Already drawn~ ♡", show_alert=False)


def register_dots_boxes_handlers(app: Client):
    app.add_handler(
        MessageHandler(
            cmd_dots,
            filters.command(["dots", "boxes"]) & filters.group,
        ),
        group=540,
    )

    app.add_handler(
        MessageHandler(
            cmd_end,
            filters.command(["enddots", "stopdots", "endboxes"]) & filters.group,
        ),
        group=540,
    )

    app.add_handler(
        MessageHandler(
            cmd_rules,
            filters.command(["dotsrules", "boxesrules"]) & filters.group,
        ),
        group=540,
    )

    app.add_handler(CallbackQueryHandler(cb_join, filters.regex("^db_join$")), group=540)
    app.add_handler(CallbackQueryHandler(cb_start, filters.regex("^db_start$")), group=540)
    app.add_handler(CallbackQueryHandler(cb_cancel, filters.regex("^db_cancel$")), group=540)
    app.add_handler(CallbackQueryHandler(cb_h, filters.regex(r"^dbh_\d+_\d+$")), group=540)
    app.add_handler(CallbackQueryHandler(cb_v, filters.regex(r"^dbv_\d+_\d+$")), group=540)
    app.add_handler(CallbackQueryHandler(cb_end, filters.regex("^db_end$")), group=540)
    app.add_handler(CallbackQueryHandler(cb_noop, filters.regex("^db_noop$")), group=540)