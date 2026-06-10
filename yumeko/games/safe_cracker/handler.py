# ==========================================================
#  Yumeko Games Bot — Safe Cracker Handler
#  Copyright (c) 2026 Jass  |  Version 2.0.1
# ==========================================================

import asyncio

from pyrogram import Client, filters
from pyrogram.enums import ChatType, ParseMode
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.types import Message, CallbackQuery

from yumeko.database.users import add_user, add_win, add_loss
from yumeko.database.groups import add_group, add_group_game, record_game_result
from yumeko.games.safe_cracker import strings as S
from yumeko.games.safe_cracker.game import (
    create_game,
    get_game,
    end_game,
    join_game,
    format_players,
    all_done,
    add_symbol,
    remove_last,
    clear_build,
    submit_guess,
    join_buttons,
    panel_buttons,
    done_panel_buttons,
    MIN_PLAYERS,
    JOIN_TIMEOUT,
    REWARD_COINS,
    REWARD_XP,
    GENIUS_BONUS,
    SHARP_BONUS,
    LOSER_XP,
)


_panel_msgs: dict[tuple, int] = {}


async def cmd_safecracker(client: Client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        await message.reply_text("🔐 Safe Cracker can only be played in groups.")
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

    create_game(chat_id, user.id, user.first_name or "Player")
    join_game(chat_id, user)
    game = get_game(chat_id)

    msg = await message.reply_text(
        S.lobby_text(
            user.first_name or "Player",
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

    game["status"] = "running"

    await message.edit_text(
        S.game_start_text(len(game["players"])),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

    await asyncio.sleep(2)

    for uid, player in game["players"].items():
        try:
            panel_msg = await client.send_message(
                chat_id,
                S.panel_text(
                    player["name"],
                    player["guesses_left"],
                    player["current_build"],
                    player["history"],
                ),
                reply_markup=panel_buttons(player["current_build"]),
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
            _panel_msgs[(chat_id, uid)] = panel_msg.id
        except Exception:
            pass


async def _refresh_panel(
    client: Client,
    chat_id: int,
    user_id: int,
    done: bool = False,
):
    game = get_game(chat_id)

    if not game:
        return

    player = game["players"].get(user_id)

    if not player:
        return

    msg_id = _panel_msgs.get((chat_id, user_id))

    if not msg_id:
        return

    caption = S.panel_text(
        player["name"],
        player["guesses_left"],
        player["current_build"],
        player["history"],
    )

    markup = done_panel_buttons() if done else panel_buttons(player["current_build"])

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


async def _check_all_done(client: Client, chat_id: int):
    game = get_game(chat_id)

    if not game or game["status"] != "running":
        return

    if not all_done(game):
        return

    await _finish_game(client, chat_id)


async def _finish_game(client: Client, chat_id: int):
    game = get_game(chat_id)

    if not game:
        return

    game["status"] = "ended"
    players = game["players"]
    code = game["code"]

    winner_id = game.get("winner_id")

    if not winner_id:
        await client.send_message(
            chat_id,
            S.no_winner_text(code),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )

        for uid in players:
            await add_loss(uid, xp=LOSER_XP)

        end_game(chat_id)
        return

    winner = players[winner_id]
    guesses_used = winner["guesses_used"]

    bonus = 0

    if guesses_used <= 3:
        bonus = GENIUS_BONUS
    elif guesses_used <= 5:
        bonus = SHARP_BONUS

    coins = REWARD_COINS + bonus

    await add_win(winner_id, coins=coins, xp=REWARD_XP)

    for uid in players:
        if uid != winner_id:
            await add_loss(uid, xp=LOSER_XP)

    await add_group_game(chat_id, game_type="safe_cracker")
    await record_game_result(
        chat_id,
        "safe_cracker",
        winner_id,
        winner["name"],
        len(players),
        extra={
            "guesses_used": guesses_used,
            "bonus": bonus,
        },
    )

    await client.send_message(
        chat_id,
        S.victory_text(
            winner["name"],
            code,
            guesses_used,
            coins,
            REWARD_XP,
            LOSER_XP,
        ),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

    end_game(chat_id)


async def cb_sc_join(client: Client, callback: CallbackQuery):
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

    await callback.answer("🔐 Joined! Ready your deduction skills~ ♡")

    game = get_game(chat_id)

    await callback.message.edit_text(
        S.lobby_updated(
            game["host_name"],
            format_players(game),
            len(game["players"]),
        ),
        reply_markup=join_buttons(),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


async def cb_sc_start(client: Client, callback: CallbackQuery):
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

    if game["status"] != "joining":
        await callback.answer("⚡ Already running~", show_alert=True)
        return

    if len(game["players"]) < MIN_PLAYERS:
        await callback.answer(S.NOT_ENOUGH, show_alert=True)
        return

    await callback.answer("🔐 Locking the safe~ ♡")

    game["status"] = "starting"
    await _launch(client, callback.message, chat_id)


async def cb_sc_cancel(client: Client, callback: CallbackQuery):
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


async def cb_sc_symbol(client: Client, callback: CallbackQuery):
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

    if game["players"][user_id]["done"]:
        await callback.answer(S.ALREADY_DONE, show_alert=True)
        return

    symbol = callback.data.replace("sc_sym_", "", 1)
    player = game["players"][user_id]

    if len(player["current_build"]) >= S.CODE_LENGTH:
        await callback.answer("🔐 4 symbols max~ Submit or clear~ ♡")
        return

    add_symbol(chat_id, user_id, symbol)

    await callback.answer(f"{symbol} added~ ♡")
    await _refresh_panel(client, chat_id, user_id)


async def cb_sc_delete(client: Client, callback: CallbackQuery):
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

    removed = remove_last(chat_id, user_id)

    await callback.answer("⌫ Removed~" if removed else "Nothing to remove~")

    if removed:
        await _refresh_panel(client, chat_id, user_id)


async def cb_sc_clear(client: Client, callback: CallbackQuery):
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

    clear_build(chat_id, user_id)

    await callback.answer("🗑 Cleared~ ♡")
    await _refresh_panel(client, chat_id, user_id)


async def cb_sc_submit(client: Client, callback: CallbackQuery):
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

    if game["players"][user_id]["done"]:
        await callback.answer(S.ALREADY_DONE, show_alert=True)
        return

    player = game["players"][user_id]

    if len(player["current_build"]) < S.CODE_LENGTH:
        await callback.answer(S.NEED_4_SYMBOLS, show_alert=True)
        return

    result = submit_guess(chat_id, user_id)

    if result["result"] == "win":
        await callback.answer("🏆 YOU CRACKED IT~ ♡", show_alert=True)
        await _refresh_panel(client, chat_id, user_id, done=True)

        await client.send_message(
            chat_id,
            f"<blockquote>🔐 <b>SAFE CRACKED!</b></blockquote>\n\n"
            f"<i>❝ Ahahaha~ <b>{player['name']}</b> cracked it~ ♡ ❞</i>\n\n"
            f"Guesses used: <b>{result['guesses_used']}</b>",
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )

        await _finish_game(client, chat_id)
        return

    if result["result"] == "eliminated":
        await callback.answer("💀 Out of guesses~ ♡", show_alert=True)
        await _refresh_panel(client, chat_id, user_id, done=True)

        await client.send_message(
            chat_id,
            S.eliminated_text(player["name"], game["code"]),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )

        await _check_all_done(client, chat_id)
        return

    bulls = result["bulls"]
    cows = result["cows"]

    fb = S.guess_feedback(
        player["name"],
        result["guess"],
        bulls,
        cows,
        result["guesses_left"],
    )

    await callback.answer(
        f"🟩 {bulls} correct  🟨 {cows} misplaced — {result['guesses_left']} left~",
        show_alert=False,
    )

    if fb:
        await client.send_message(
            chat_id,
            fb,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )

    await _refresh_panel(client, chat_id, user_id)
    await _check_all_done(client, chat_id)


async def cb_sc_noop(client: Client, callback: CallbackQuery):
    await callback.answer()
async def cmd_end_safecracker(client: Client, message: Message):
    if not message.from_user:
        return

    chat_id = message.chat.id
    game = get_game(chat_id)

    if not game:
        await message.reply_text("❌ No Safe Cracker game is active.")
        return

    if (
        message.from_user.id != game["host_id"]
        and message.from_user.id not in game["players"]
    ):
        await message.reply_text("🚫 Only players can end this game.")
        return

    end_game(chat_id)

    await message.reply_text(
        "<blockquote>🛑 <b>SAFE CRACKER ENDED</b></blockquote>\n\n"
        "<i>❝ The vault closes once more~ ♡ ❞</i>",
        parse_mode=ParseMode.HTML,
    )

def register_safe_cracker_handlers(app: Client):
    app.add_handler(
        MessageHandler(
            cmd_safecracker,
            filters.command(["safecracker", "safe", "crack"]) & filters.group,
        ),
        group=480,
    )

    app.add_handler(CallbackQueryHandler(cb_sc_join, filters.regex("^sc_join$")), group=480)
    app.add_handler(CallbackQueryHandler(cb_sc_start, filters.regex("^sc_start$")), group=480)
    app.add_handler(CallbackQueryHandler(cb_sc_cancel, filters.regex("^sc_cancel$")), group=480)
    app.add_handler(CallbackQueryHandler(cb_sc_symbol, filters.regex(r"^sc_sym_")), group=480)
    app.add_handler(CallbackQueryHandler(cb_sc_delete, filters.regex("^sc_delete$")), group=480)
    app.add_handler(CallbackQueryHandler(cb_sc_clear, filters.regex("^sc_clear$")), group=480)
    app.add_handler(CallbackQueryHandler(cb_sc_submit, filters.regex("^sc_submit$")), group=480)
    app.add_handler(CallbackQueryHandler(cb_sc_noop, filters.regex("^sc_noop$")), group=480)
    app.add_handler(
    MessageHandler(
        cmd_end_safecracker,
        filters.command(
            ["endsafe", "stopsafe", "endsafecracker"]
        ) & filters.group,
    ),
    group=480,
)