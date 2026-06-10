# ==========================================================
#  Yumeko Games Bot — Battleship Royale Handler
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

from yumeko.games.battleship import strings as S
from yumeko.games.battleship.game import (
    create_game,
    get_game,
    end_game,
    join_game,
    start_game,
    attack,
    current_player,
    opponent_player,
    format_players,
    own_board_text,
    enemy_board_text,
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
            [InlineKeyboardButton("🎮 Join Battle", callback_data="bs_join")],
            [
                InlineKeyboardButton("▶️ Start", callback_data="bs_start"),
                InlineKeyboardButton("🛑 Cancel", callback_data="bs_cancel"),
            ],
        ]
    )


def board_buttons(game):
    rows = []

    current = current_player(game)
    enemy = opponent_player(game, current["id"])

    for r in range(BOARD_SIZE):
        row = []

        for c in range(BOARD_SIZE):
            cell = enemy["board"][r][c]

            if cell["hit"]:
                text = "💥"
            elif cell["miss"]:
                text = "⭕"
            else:
                text = "⬛"

            row.append(
                InlineKeyboardButton(
                    text,
                    callback_data=f"bs_fire_{r}_{c}",
                )
            )

        rows.append(row)

    rows.append([InlineKeyboardButton("🛑 End Battle", callback_data="bs_end")])
    return InlineKeyboardMarkup(rows)


async def cmd_battleship(client: Client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        await message.reply_text("🚢 Battleship can only be played in groups.")
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


async def cmd_battle_rules(client: Client, message: Message):
    await message.reply_text(
        S.rules_text(),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


async def cmd_end_battle(client: Client, message: Message):
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
        await message.reply_text("Only players can end this Battleship match.")
        return

    end_game(chat_id)

    await message.reply_text(
        "<blockquote>🛑 <b>Battleship Ended</b></blockquote>\n\n"
        "<i>❝ The fleet returns to harbor~ ♡ ❞</i>",
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
            "started": "⚡ Battle already started.",
            "joined": S.ALREADY_JOINED,
            "full": S.GAME_FULL,
        }
        await callback.answer(msgs.get(reason, "Cannot join."), show_alert=True)
        return

    await callback.answer("🚢 Fleet joined~ ♡")

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
    enemy = opponent_player(game, current["id"])

    await callback.answer("Battle started~ ♡")

    await callback.message.edit_text(
        S.arena_text(
            current["name"],
            enemy_board_text(enemy),
            own_board_text(current),
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


async def finish_game(callback: CallbackQuery, game, winner_id):
    winner = game["players"][winner_id]

    await add_win(winner_id, coins=WIN_COINS, xp=WIN_XP)

    for uid in game["players"]:
        if uid != winner_id:
            await add_loss(uid, xp=LOSE_XP)

    await callback.message.edit_text(
        S.winner_text(
            winner["name"],
            final_scoreboard(game),
            WIN_COINS,
            WIN_XP,
        ),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

    end_game(callback.message.chat.id)


async def cb_fire(client: Client, callback: CallbackQuery):
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
        await callback.answer("Invalid coordinate.", show_alert=True)
        return

    ok, reason, result = attack(chat_id, user.id, row, col)

    if not ok:
        msgs = {
            "not_turn": S.NOT_YOUR_TURN,
            "already": S.ALREADY_ATTACKED,
            "not_player": S.NOT_PLAYER,
            "not_playing": "Battle has not started.",
        }
        await callback.answer(msgs.get(reason, "Cannot fire."), show_alert=True)
        return

    game = get_game(chat_id)
    attacker = result["attacker"]

    if result["game_over"]:
        await callback.answer("🏆 Victory!", show_alert=True)
        await finish_game(callback, game, result["winner"])
        return

    if result["hit"]:
        await callback.answer("💥 HIT! Fire again~", show_alert=True)
    else:
        await callback.answer("⭕ Miss~")

    current = current_player(game)
    enemy = opponent_player(game, current["id"])

    text = S.attack_text(
        attacker["name"],
        row,
        col,
        "hit" if result["hit"] else "miss",
    )

    if result["sunk"]:
        text += "\n\n" + S.sunk_text(result["sunk"]["name"])

    text += "\n\n" + S.arena_text(
        current["name"],
        enemy_board_text(enemy),
        own_board_text(current),
    )

    await callback.message.edit_text(
        text,
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

    await callback.answer("Battle ended.")
    await callback.message.edit_text(
        "<blockquote>🛑 <b>Battleship Ended</b></blockquote>\n\n"
        "<i>❝ Yumeko lets the sea sleep again~ ♡ ❞</i>",
        parse_mode=ParseMode.HTML,
    )


def register_battleship_handlers(app: Client):
    app.add_handler(
        MessageHandler(
            cmd_battleship,
            filters.command(["battleship", "seabattle", "sea"]) & filters.group,
        ),
        group=500,
    )

    app.add_handler(
        MessageHandler(
            cmd_end_battle,
            filters.command(["endbattle", "stopbattle", "endsea"]) & filters.group,
        ),
        group=500,
    )

    app.add_handler(
        MessageHandler(
            cmd_battle_rules,
            filters.command(["battlerules", "searules"]) & filters.group,
        ),
        group=500,
    )

    app.add_handler(CallbackQueryHandler(cb_join, filters.regex("^bs_join$")), group=500)
    app.add_handler(CallbackQueryHandler(cb_start, filters.regex("^bs_start$")), group=500)
    app.add_handler(CallbackQueryHandler(cb_cancel, filters.regex("^bs_cancel$")), group=500)
    app.add_handler(CallbackQueryHandler(cb_fire, filters.regex(r"^bs_fire_\d+_\d+$")), group=500)
    app.add_handler(CallbackQueryHandler(cb_end, filters.regex("^bs_end$")), group=500)