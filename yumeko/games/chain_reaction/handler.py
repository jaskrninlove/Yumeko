# ==========================================================
#  Yumeko Games Bot — Chain Reaction Handler
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

import asyncio
from pyrogram.errors import FloodWait, MessageNotModified
from yumeko.database.users import add_user, add_win, add_loss
from yumeko.database.groups import add_group

from yumeko.games.chain_reaction import strings as S
from yumeko.games.chain_reaction.game import (
    create_game,
    get_game,
    end_game,
    join_game,
    start_game,
    make_move,
    current_player,
    alive_players,
    format_players,
    board_text,
    final_scoreboard,
    MIN_PLAYERS,
    MAX_PLAYERS,
    ROWS,
    COLS,
    WIN_COINS,
    WIN_XP,
    LOSE_XP,
)

async def safe_edit(message, text, reply_markup=None):
    try:
        return await message.edit_text(
            text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
    except MessageNotModified:
        return None
    except FloodWait as e:
        await asyncio.sleep(e.value + 1)
        try:
            return await message.edit_text(
                text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
        except Exception:
            return None
    except Exception:
        return None

def lobby_buttons():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🎮 Join Game", callback_data="cr_join")],
            [
                InlineKeyboardButton("▶️ Start", callback_data="cr_start"),
                InlineKeyboardButton("🛑 Cancel", callback_data="cr_cancel"),
            ],
        ]
    )


def board_buttons(game):
    rows = []

    for r in range(ROWS):
        row = []

        for c in range(COLS):
            cell = game["board"][r][c]

            if not cell["owner"] or cell["count"] == 0:
                text = "⬛"
            else:
                player = game["players"].get(cell["owner"])
                orb = player["orb"] if player else "⚫"
                text = orb if cell["count"] == 1 else f"{orb}{cell['count']}"

            row.append(
                InlineKeyboardButton(
                    text,
                    callback_data=f"cr_move_{r}_{c}",
                )
            )

        rows.append(row)

    rows.append([InlineKeyboardButton("🛑 End Game", callback_data="cr_end")])
    return InlineKeyboardMarkup(rows)


async def cmd_chain_reaction(client: Client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        await message.reply_text("⚛ Chain Reaction can only be played in groups.")
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


async def cmd_chain_rules(client: Client, message: Message):
    await message.reply_text(
        S.rules_text(),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


async def cmd_end_chain(client: Client, message: Message):
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
        await message.reply_text("Only players can end this Chain Reaction game.")
        return

    end_game(chat_id)

    await message.reply_text(
        "<blockquote>🛑 <b>Chain Reaction Ended</b></blockquote>\n\n"
        "<i>❝ The unstable orbs go quiet for now~ ♡ ❞</i>",
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
            "started": "⚡ Game already started.",
            "joined": S.ALREADY_JOINED,
            "full": S.GAME_FULL,
        }
        await callback.answer(msgs.get(reason, "Cannot join."), show_alert=True)
        return

    await callback.answer("⚛ Joined the reaction chamber~ ♡")

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

    await callback.answer("Reaction started~ ♡")

    await callback.message.edit_text(
        S.arena_text(
            board_text(game),
            current["name"],
            current["orb"],
            game["round"],
            len(alive_players(game)),
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
    await safe_edit(callback.message, S.GAME_CANCELLED)


async def finish_game(callback: CallbackQuery, game, winner_id):
    if not winner_id:
        await callback.message.edit_text(
            S.no_winner_text(),
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
            winner["orb"],
            final_scoreboard(game),
            WIN_COINS,
            WIN_XP,
        ),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

    end_game(callback.message.chat.id)


async def cb_move(client: Client, callback: CallbackQuery):
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
        await callback.answer("Invalid cell.", show_alert=True)
        return

    ok, reason, result = make_move(chat_id, user.id, row, col)

    if not ok:
        msgs = {
            "not_turn": S.NOT_YOUR_TURN,
            "dead": S.ALREADY_DEAD,
            "not_player": S.NOT_PLAYER,
            "enemy_cell": S.ENEMY_CELL,
            "not_playing": "Game has not started.",
        }
        await callback.answer(msgs.get(reason, "Cannot place orb."), show_alert=True)
        return

    game = get_game(chat_id)
    player = result["player"]

    await callback.answer("Orb placed~ ♡")

    if result["game_over"]:
        await finish_game(callback, game, result["winner"])
        return

    current = current_player(game)

    eliminated_names = [
        game["players"][uid]["name"]
        for uid in result["eliminated"]
        if uid in game["players"]
    ]

    await safe_edit(
      callback.message,
      S.move_text(
        player["name"],
        player["orb"],
        row,
        col,
        result["explosions"],
        eliminated_names,
      )
      + S.arena_text(
        board_text(game),
        current["name"],
        current["orb"],
        game["round"],
        len(alive_players(game)),
      ),
      reply_markup=board_buttons(game),
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

    await callback.answer("Game ended.")
    await callback.message.edit_text(
        "<blockquote>🛑 <b>Chain Reaction Ended</b></blockquote>\n\n"
        "<i>❝ Yumeko lets the orbs sleep again~ ♡ ❞</i>",
        parse_mode=ParseMode.HTML,
    )


def register_chain_reaction_handlers(app: Client):
    app.add_handler(
        MessageHandler(
            cmd_chain_reaction,
            filters.command(["chainreaction", "chain"]) & filters.group,
        ),
        group=460,
    )

    app.add_handler(
        MessageHandler(
            cmd_end_chain,
            filters.command(["endchain", "stopchain"]) & filters.group,
        ),
        group=460,
    )

    app.add_handler(
        MessageHandler(
            cmd_chain_rules,
            filters.command(["chainrules", "reactionrules"]) & filters.group,
        ),
        group=460,
    )

    app.add_handler(CallbackQueryHandler(cb_join, filters.regex("^cr_join$")), group=460)
    app.add_handler(CallbackQueryHandler(cb_start, filters.regex("^cr_start$")), group=460)
    app.add_handler(CallbackQueryHandler(cb_cancel, filters.regex("^cr_cancel$")), group=460)
    app.add_handler(CallbackQueryHandler(cb_move, filters.regex(r"^cr_move_\d+_\d+$")), group=460)
    app.add_handler(CallbackQueryHandler(cb_end, filters.regex("^cr_end$")), group=460)