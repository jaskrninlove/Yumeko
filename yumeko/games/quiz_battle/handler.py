# ==========================================================
#  Yumeko Games Bot — Quiz Battle Handler
#  Copyright (c) 2026 Jass  |  Version 2.0.1
# ==========================================================

import asyncio
import time

from pyrogram import Client, filters
from pyrogram.enums import ChatType, ParseMode
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.types import Message, CallbackQuery

from yumeko.database.users import add_user
from yumeko.database.groups import add_group
from yumeko.games.quiz_battle import strings as S
from yumeko.games.quiz_battle.game import (
    create_game,
    get_game,
    end_game,
    join_game,
    format_players,
    join_buttons,
    run_game,
    MIN_PLAYERS,
    JOIN_TIMEOUT,
    POINTS_FIRST,
    POINTS_SECOND,
    POINTS_WRONG,
    SPEED_BONUS_S,
)


async def cmd_quiz(client: Client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        await message.reply_text("🧠 Quiz Battle can only be played in groups.")
        return

    if not message.from_user:
        return

    await add_user(message.from_user)
    await add_group(message.chat)

    chat_id = message.chat.id
    user = message.from_user

    if get_game(chat_id):
        await message.reply_text(S.ALREADY_RUNNING)
        return

    create_game(chat_id, user.id, user.first_name or "Unknown")
    join_game(chat_id, user)
    game = get_game(chat_id)

    msg = await message.reply_text(
        S.lobby_text(
            user.first_name or "Unknown",
            format_players(game),
            len(game["players"]),
            JOIN_TIMEOUT,
        ),
        reply_markup=join_buttons(),
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
    await _launch(client, msg, chat_id)


async def _launch(client: Client, message: Message, chat_id: int):
    game = get_game(chat_id)

    if not game:
        return

    await message.edit_text(
        (
            "<blockquote>🧠 <b>Quiz Battle Starting!</b></blockquote>\n\n"
            f"<i>❝ {len(game['players'])} minds enter~ One champion leaves~ ♡ ❞</i>\n\n"
            f"{format_players(game)}\n\n"
            "<i>Round 1 begins in 3 seconds...</i>"
        ),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

    await asyncio.sleep(3)
    await run_game(client, message, chat_id)


async def cb_qz_join(client: Client, callback: CallbackQuery):
    if not callback.message:
        return

    await add_user(callback.from_user)

    chat_id = callback.message.chat.id
    user = callback.from_user
    game = get_game(chat_id)

    if not game:
        await callback.answer("❌ No active quiz.", show_alert=True)
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

    await callback.answer("🧠 Joined! Sharpen that brain~ ♡", show_alert=False)

    game = get_game(chat_id)

    await callback.message.edit_text(
        S.lobby_text(
            game["host_name"],
            format_players(game),
            len(game["players"]),
            JOIN_TIMEOUT,
        ),
        reply_markup=join_buttons(),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


async def cb_qz_start(client: Client, callback: CallbackQuery):
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
        await callback.answer("⚡ Already started~", show_alert=True)
        return

    if len(game["players"]) < MIN_PLAYERS:
        await callback.answer(S.NOT_ENOUGH, show_alert=True)
        return

    await callback.answer("🧠 Starting~ ♡", show_alert=False)

    game["status"] = "starting"
    await _launch(client, callback.message, chat_id)


async def cb_qz_cancel(client: Client, callback: CallbackQuery):
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

    await callback.answer("❌ Cancelled.", show_alert=False)

    await callback.message.edit_text(
        S.GAME_CANCELLED,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


async def cb_qz_answer(client: Client, callback: CallbackQuery):
    if not callback.message:
        return

    chat_id = callback.message.chat.id
    user_id = callback.from_user.id
    game = get_game(chat_id)

    if not game or not game.get("round_open"):
        await callback.answer("⌛ Round already closed~", show_alert=False)
        return

    if user_id not in game["players"]:
        await callback.answer("🚫 You're not in this quiz~", show_alert=True)
        return

    if user_id in game["round_answered"]:
        await callback.answer("✅ Already answered this round~ ♡", show_alert=False)
        return

    try:
        idx = int(callback.data.split("_ans_")[1])
    except Exception:
        await callback.answer("❌ Invalid answer.", show_alert=False)
        return

    game["round_answered"].add(user_id)

    correct = game["round_correct_idx"]
    start_t = game["round_start_time"] or time.time()
    elapsed = time.time() - start_t
    elapsed_ms = int(elapsed * 1000)

    name = game["players"][user_id]["name"]

    q_data = game["questions"][game["round"] - 1]
    options = q_data[1]

    if idx == correct:
        is_first = game.get("first_correct") is None
        speed_ok = elapsed <= SPEED_BONUS_S

        if is_first:
            game["first_correct"] = user_id
            pts = POINTS_FIRST + (1 if speed_ok else 0)
            game["scores"][user_id] = game["scores"].get(user_id, 0) + pts

            await callback.answer(
                S.correct_first(
                    name,
                    options[correct],
                    elapsed_ms,
                    speed_ok,
                ),
                show_alert=False,
            )
        else:
            game["scores"][user_id] = (
                game["scores"].get(user_id, 0) + POINTS_SECOND
            )

            await callback.answer(
                S.correct_later(
                    name,
                    POINTS_SECOND,
                ),
                show_alert=False,
            )
    else:
        game["scores"][user_id] = (
            game["scores"].get(user_id, 0) + POINTS_WRONG
        )

        await callback.answer(
            S.wrong_answer(name),
            show_alert=False,
        )

async def end_quiz_cmd(client: Client, message: Message):
    if not message.from_user:
        return

    chat_id = message.chat.id
    game = get_game(chat_id)

    if not game:
        await message.reply_text(
            "🧠 No Quiz Battle is currently running."
        )
        return

    user_id = message.from_user.id

    if user_id != game["host_id"]:
        await message.reply_text(
            "⚡ Only the quiz host can end this game."
        )
        return

    end_game(chat_id)

    await message.reply_text(
        "<blockquote>🛑 <b>Quiz Battle Ended</b></blockquote>\n\n"
        f"👤 Ended by <b>{message.from_user.first_name}</b>\n\n"
        "<i>❝ The battle of minds comes to an end~ ♡ ❞</i>",
        parse_mode=ParseMode.HTML,
    )

def register_quiz_battle_handlers(app: Client):
    app.add_handler(
        MessageHandler(
            cmd_quiz,
            filters.command(["quiz", "quizbattle"]) & filters.group,
        ),
        group=370,
    )

    app.add_handler(
        CallbackQueryHandler(
            cb_qz_join,
            filters.regex("^qz_join$"),
        ),
        group=370,
    )

    app.add_handler(
        CallbackQueryHandler(
            cb_qz_start,
            filters.regex("^qz_start$"),
        ),
        group=370,
    )

    app.add_handler(
        CallbackQueryHandler(
            cb_qz_cancel,
            filters.regex("^qz_cancel$"),
        ),
        group=370,
    )

    app.add_handler(
        CallbackQueryHandler(
            cb_qz_answer,
            filters.regex(r"^qz_ans_\d+$"),
        ),
        group=370,
    )
    app.add_handler(
        MessageHandler(
            end_quiz_cmd,
            filters.command(
                ["endquiz", "stopquiz"]
            ) & filters.group,
        ),
        group=370,
    )