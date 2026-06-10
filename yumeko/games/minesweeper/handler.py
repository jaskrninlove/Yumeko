# ==========================================================
#  Yumeko Games Bot — Minesweeper Handler
#  Copyright (c) 2026 Jass  |  Version 2.0.1
# ==========================================================

import asyncio

from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery

from yumeko.database.users import add_user, add_win, add_loss
from yumeko.database.groups import add_group, add_group_game, record_game_result
from yumeko.games.minesweeper import strings as S
from yumeko.games.minesweeper.game import (
    create_game, get_game, end_game, join_game,
    reveal_cell, toggle_flag, format_players,
    is_game_over, get_winner, join_buttons, board_buttons,
    spectate_board_buttons, REWARD_COINS, REWARD_XP,
    LOSER_XP, PERFECT_BONUS, MIN_PLAYERS, JOIN_TIMEOUT,
    DIFFICULTIES,
)


def _is_group(_, __, m):
    return m.chat.type.name in ("GROUP", "SUPERGROUP")


group_filter = filters.create(_is_group)

_flag_modes: dict[int, bool] = {}
_board_msgs: dict[tuple, int] = {}


async def cmd_minesweeper(client: Client, message: Message):
    if not message.from_user:
        return

    await add_user(message.from_user)
    await add_group(message.chat)

    chat_id = message.chat.id
    user = message.from_user

    if get_game(chat_id):
        await message.reply_text(S.ALREADY_RUNNING)
        return

    create_game(chat_id, user.id, user.first_name or "Player")
    join_game(chat_id, user)
    game = get_game(chat_id)

    msg = await message.reply_text(
        S.lobby_text(
            user.first_name or "Player",
            format_players(game),
            len(game["players"]),
            JOIN_TIMEOUT,
            game["mode"],
        ),
        reply_markup=join_buttons(game["mode"]),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

    await asyncio.sleep(JOIN_TIMEOUT)

    game = get_game(chat_id)

    if not game or game["status"] != "joining":
        return

    if len(game["players"]) < MIN_PLAYERS:
        end_game(chat_id)
        await msg.edit_text(
            S.NOT_ENOUGH,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
        return

    game["status"] = "starting"
    await _launch_game(client, msg, chat_id)


def _reveal_board_button() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("💎 Open My Board", callback_data="ms_open_board")]]
    )


async def _launch_game(client: Client, message: Message, chat_id: int):
    game = get_game(chat_id)

    if not game:
        return

    game["status"] = "running"

    diff_name = game["difficulty"].capitalize()
    rows, cols, mines = game["rows"], game["cols"], game["mine_count"]

    await message.edit_text(
        f"<blockquote>💎 <b>MINESWEEPER STARTS!</b></blockquote>\n\n"
        f"<i>❝ The field is set~ {rows}×{cols} grid~ {mines} mines~ ♡ ❞</i>\n\n"
        f"🎮 Difficulty: <b>{diff_name}</b>\n"
        f"👥 Players: <b>{len(game['players'])}</b>\n\n"
        f"<b>Each player gets their own board~</b>\n"
        f"<i>Tap the button below to reveal yours~ ♡</i>",
        reply_markup=_reveal_board_button(),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

    for uid, player in game["players"].items():
        try:
            flag_mode = _flag_modes.get(uid, False)

            board_msg = await client.send_message(
                chat_id,
                S.board_caption(
                    player["name"],
                    0,
                    0,
                    flags_left=game["mine_count"],
                    lives=player["lives"],
                ),
                reply_markup=board_buttons(chat_id, uid, flag_mode),
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )

            _board_msgs[(chat_id, uid)] = board_msg.id
        except Exception:
            pass


async def _refresh_board(
    client: Client,
    chat_id: int,
    user_id: int,
    status: str = "playing",
):
    game = get_game(chat_id)

    if not game:
        return

    player = game["players"].get(user_id)

    if not player:
        return

    msg_id = _board_msgs.get((chat_id, user_id))

    if not msg_id:
        return

    flag_mode = _flag_modes.get(user_id, False)

    flags_used = sum(
        1
        for r in range(game["rows"])
        for c in range(game["cols"])
        if player["flagged"][r][c]
    )

    flags_left = game["mine_count"] - flags_used

    caption = S.board_caption(
        player["name"],
        player["safe_count"],
        player["total_safe"] or 1,
        flags_left,
        player["lives"],
        status,
    )

    markup = (
        board_buttons(chat_id, user_id, flag_mode)
        if player["alive"]
        else spectate_board_buttons(chat_id, user_id)
    )

    try:
        await client.edit_message_text(
            chat_id,
            msg_id,
            caption,
            reply_markup=markup,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
    except Exception:
        pass


async def _check_game_over(client: Client, chat_id: int):
    game = get_game(chat_id)

    if not game or game["status"] != "running":
        return

    if not is_game_over(game):
        return

    winner_id = get_winner(game)
    await _finish_game(client, chat_id, winner_id)


async def _finish_game(client: Client, chat_id: int, winner_id):
    game = get_game(chat_id)

    if not game:
        return

    game["status"] = "ended"

    if not winner_id:
        await client.send_message(
            chat_id,
            S.no_winner_text(),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )

        for uid in game["players"]:
            await add_loss(uid, xp=LOSER_XP)

        end_game(chat_id)
        return

    winner = game["players"][winner_id]
    safe = winner["safe_count"]
    total = winner["total_safe"]
    is_perfect = total > 0 and safe >= total

    bonus = PERFECT_BONUS if is_perfect else 0
    coins = REWARD_COINS + bonus

    await add_win(winner_id, coins=coins, xp=REWARD_XP)

    for uid in game["players"]:
        if uid != winner_id:
            await add_loss(uid, xp=LOSER_XP)

    await add_group_game(chat_id, game_type="minesweeper")
    await record_game_result(
        chat_id,
        "minesweeper",
        winner_id,
        winner["name"],
        len(game["players"]),
        extra={"safe": safe, "perfect": is_perfect},
    )

    scores = [
        (p["name"], p["safe_count"], "alive" if p["alive"] else "dead")
        for p in game["players"].values()
    ]

    await client.send_message(
        chat_id,
        S.victory_text(
            winner["name"],
            safe,
            total,
            is_perfect,
            coins,
            REWARD_XP,
            LOSER_XP,
            S.scoreboard_text(scores),
        ),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

    end_game(chat_id)


async def cb_ms_join(client: Client, callback: CallbackQuery):
    if not callback.message:
        return

    await add_user(callback.from_user)

    chat_id = callback.message.chat.id
    user = callback.from_user
    game = get_game(chat_id)

    if not game:
        await callback.answer("❌ No active game~", show_alert=True)
        return

    ok, reason = join_game(chat_id, user)

    if not ok:
        msgs = {
            "started": "⚡ Already started~",
            "full": S.GAME_FULL,
            "joined": S.ALREADY_JOINED,
        }
        await callback.answer(msgs.get(reason, "❌ Cannot join."), show_alert=True)
        return

    await callback.answer("💎 Joined! Don't tap the mines~ ♡")

    game = get_game(chat_id)

    await callback.message.edit_text(
        S.lobby_updated(
            game["host_name"],
            format_players(game),
            len(game["players"]),
            game["mode"],
        ),
        reply_markup=join_buttons(game["mode"]),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


async def cb_ms_start(client: Client, callback: CallbackQuery):
    if not callback.message:
        return

    chat_id = callback.message.chat.id
    user = callback.from_user
    game = get_game(chat_id)

    if not game:
        await callback.answer("❌ No game.", show_alert=True)
        return

    if user.id != game["host_id"]:
        await callback.answer(S.HOST_ONLY, show_alert=True)
        return

    if game["status"] != "joining":
        await callback.answer("⚡ Already running~", show_alert=True)
        return

    if len(game["players"]) < MIN_PLAYERS:
        await callback.answer(S.NOT_ENOUGH, show_alert=True)
        return

    await callback.answer("💎 Starting~ ♡")
    game["status"] = "starting"

    await _launch_game(client, callback.message, chat_id)


async def cb_ms_cancel(client: Client, callback: CallbackQuery):
    if not callback.message:
        return

    chat_id = callback.message.chat.id
    game = get_game(chat_id)

    if not game:
        await callback.answer("❌ No game.", show_alert=True)
        return

    if callback.from_user.id != game["host_id"]:
        await callback.answer(S.HOST_ONLY, show_alert=True)
        return

    end_game(chat_id)

    await callback.answer("❌ Cancelled.")
    await callback.message.edit_text(
        S.GAME_CANCELLED,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


async def cb_ms_difficulty(client: Client, callback: CallbackQuery):
    if not callback.message:
        return

    chat_id = callback.message.chat.id
    user_id = callback.from_user.id
    game = get_game(chat_id)

    if not game:
        await callback.answer("❌ No game.", show_alert=True)
        return

    if user_id != game["host_id"]:
        await callback.answer(S.HOST_ONLY, show_alert=True)
        return

    if game["status"] != "joining":
        await callback.answer("⚡ Already started~", show_alert=True)
        return

    diff = callback.data.replace("ms_diff_", "", 1)

    if diff not in DIFFICULTIES:
        await callback.answer("❌ Invalid difficulty~", show_alert=True)
        return

    d = DIFFICULTIES[diff]

    game["difficulty"] = diff
    game["rows"] = d["rows"]
    game["cols"] = d["cols"]
    game["mine_count"] = d["mines"]

    for player in game["players"].values():
        player["board"] = None
        player["revealed"] = [[False] * d["cols"] for _ in range(d["rows"])]
        player["flagged"] = [[False] * d["cols"] for _ in range(d["rows"])]

    labels = {
        "easy": "🟢 Easy",
        "medium": "🟡 Medium",
        "hard": "🔴 Hard",
    }

    await callback.answer(f"Set to {labels.get(diff, diff)}~ ♡")

    await callback.message.edit_text(
        S.lobby_text(
            game["host_name"],
            format_players(game),
            len(game["players"]),
            JOIN_TIMEOUT,
            game["mode"],
        ),
        reply_markup=join_buttons(game["mode"]),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


async def cb_ms_open_board(client: Client, callback: CallbackQuery):
    if not callback.message:
        return

    chat_id = callback.message.chat.id
    user_id = callback.from_user.id
    game = get_game(chat_id)

    if not game or game["status"] != "running":
        await callback.answer("❌ Game not running~", show_alert=True)
        return

    if user_id not in game["players"]:
        await callback.answer(S.NOT_IN_GAME, show_alert=True)
        return

    await callback.answer("💎 Your board is already visible below~ ♡")


async def cb_ms_tap(client: Client, callback: CallbackQuery):
    if not callback.message:
        return

    chat_id = callback.message.chat.id
    user_id = callback.from_user.id
    game = get_game(chat_id)

    if not game or game["status"] != "running":
        await callback.answer("❌ No active game~")
        return

    if user_id not in game["players"]:
        await callback.answer(S.NOT_IN_GAME, show_alert=True)
        return

    player = game["players"][user_id]

    if not player["alive"]:
        await callback.answer(S.ALREADY_DEAD, show_alert=True)
        return

    try:
        _, _, row, col = callback.data.split("_")
        row = int(row)
        col = int(col)
    except Exception:
        await callback.answer("❌ Invalid cell.", show_alert=True)
        return

    result = reveal_cell(chat_id, user_id, row, col)

    if result["result"] == "already":
        await callback.answer(S.ALREADY_REVEALED)
        return

    if result["result"] == "mine":
        lives = result["lives_left"]

        if lives <= 0:
            await callback.answer(S.BOOM_EMOJI + " ELIMINATED~ ♡", show_alert=True)
            await _refresh_board(client, chat_id, user_id, "dead")

            await client.send_message(
                chat_id,
                S.player_eliminated(player["name"], player["safe_count"]),
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
        else:
            await callback.answer(f"💥 Mine! {lives} lives left~ ♡", show_alert=True)
            await _refresh_board(client, chat_id, user_id)

        await _check_game_over(client, chat_id)
        return

    if result["result"] == "win":
        await callback.answer("💎 YOU CLEARED IT~ ♡", show_alert=True)
        await _refresh_board(client, chat_id, user_id, "won")

        await client.send_message(
            chat_id,
            S.all_safe_cleared(player["name"]),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )

        await _finish_game(client, chat_id, user_id)
        return

    msg = S.safe_tap_text(player["name"], player["safe_count"])

    await callback.answer(msg or "🟩 Safe~ ♡")
    await _refresh_board(client, chat_id, user_id)


async def cb_ms_flag(client: Client, callback: CallbackQuery):
    if not callback.message:
        return

    chat_id = callback.message.chat.id
    user_id = callback.from_user.id
    game = get_game(chat_id)

    if not game or game["status"] != "running":
        await callback.answer("❌ No active game.")
        return

    if user_id not in game["players"]:
        await callback.answer(S.NOT_IN_GAME, show_alert=True)
        return

    player = game["players"][user_id]

    if not player["alive"]:
        await callback.answer(S.ALREADY_DEAD, show_alert=True)
        return

    try:
        _, _, row, col = callback.data.split("_")
        row = int(row)
        col = int(col)
    except Exception:
        await callback.answer("❌ Invalid flag.", show_alert=True)
        return

    placed = toggle_flag(chat_id, user_id, row, col)

    if placed is None:
        await callback.answer("❌ Already revealed~")
        return

    if placed:
        await callback.answer(f"🚩 Flagged ({row + 1},{col + 1})~ ♡")
    else:
        await callback.answer("✅ Flag removed~")

    await _refresh_board(client, chat_id, user_id)


async def cb_ms_unflag(client: Client, callback: CallbackQuery):
    if not callback.message:
        return

    chat_id = callback.message.chat.id
    user_id = callback.from_user.id
    game = get_game(chat_id)

    if not game or game["status"] != "running":
        await callback.answer("❌ No active game.")
        return

    try:
        _, _, row, col = callback.data.split("_")
        row = int(row)
        col = int(col)
    except Exception:
        await callback.answer("❌ Invalid cell.", show_alert=True)
        return

    toggle_flag(chat_id, user_id, row, col)

    await callback.answer("✅ Flag removed~")
    await _refresh_board(client, chat_id, user_id)


async def cb_ms_flagmode(client: Client, callback: CallbackQuery):
    if not callback.message:
        return

    user_id = callback.from_user.id
    flag_mode = "on" in callback.data
    _flag_modes[user_id] = flag_mode

    chat_id = callback.message.chat.id
    game = get_game(chat_id)

    if not game or user_id not in game["players"]:
        await callback.answer("❌")
        return

    await callback.answer("🚩 Flag Mode ON~ ♡" if flag_mode else "✅ Tap Mode~ ♡")
    await _refresh_board(client, chat_id, user_id)


async def cb_ms_noop(client: Client, callback: CallbackQuery):
    await callback.answer()


def register_minesweeper_handlers(app: Client):
    app.add_handler(
        MessageHandler(
            cmd_minesweeper,
            filters.command(["minesweeper", "ms", "mine"]) & group_filter,
        ),
        group=440,
    )

    app.add_handler(CallbackQueryHandler(cb_ms_join, filters.regex("^ms_join$")), group=440)
    app.add_handler(CallbackQueryHandler(cb_ms_start, filters.regex("^ms_start$")), group=440)
    app.add_handler(CallbackQueryHandler(cb_ms_cancel, filters.regex("^ms_cancel$")), group=440)
    app.add_handler(CallbackQueryHandler(cb_ms_difficulty, filters.regex(r"^ms_diff_")), group=440)
    app.add_handler(CallbackQueryHandler(cb_ms_open_board, filters.regex("^ms_open_board$")), group=440)
    app.add_handler(CallbackQueryHandler(cb_ms_tap, filters.regex(r"^ms_tap_\d+_\d+$")), group=440)
    app.add_handler(CallbackQueryHandler(cb_ms_flag, filters.regex(r"^ms_flag_\d+_\d+$")), group=440)
    app.add_handler(CallbackQueryHandler(cb_ms_unflag, filters.regex(r"^ms_unflag_\d+_\d+$")), group=440)
    app.add_handler(CallbackQueryHandler(cb_ms_flagmode, filters.regex(r"^ms_flagmode_")), group=440)
    app.add_handler(CallbackQueryHandler(cb_ms_noop, filters.regex("^ms_noop$")), group=440)