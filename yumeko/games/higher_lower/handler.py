# ==========================================================
#  Yumeko Games Bot — Higher or Lower Handler
#  Copyright (c) 2026 Jass  |  Version 2.0.1
# ==========================================================

import asyncio

from pyrogram import Client, filters
from pyrogram.enums import ChatType, ParseMode
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.types import Message, CallbackQuery

from yumeko.database.users import add_user, add_win, add_loss
from yumeko.database.groups import add_group, add_group_game, record_game_result
from yumeko.games.higher_lower import strings as S
from yumeko.games.higher_lower.game import (
    create_game,
    get_game,
    end_game,
    join_game,
    alive_players,
    format_players,
    join_buttons,
    vote_buttons,
    vote_buttons_voted,
    resolve_round,
    _draw,
    MIN_PLAYERS,
    JOIN_TIMEOUT,
    TOTAL_ROUNDS,
    ROUND_TIMEOUT,
    REWARD_COINS,
    REWARD_XP,
    LOSER_XP,
)


_round_msgs: dict[int, int] = {}


async def cmd_higherorlower(client: Client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        await message.reply_text(
            S.GROUPS_ONLY,
            parse_mode=ParseMode.HTML,
        )
        return

    if not message.from_user:
        return

    await add_user(message.from_user)
    await add_group(message.chat)

    chat_id = message.chat.id
    user = message.from_user

    if get_game(chat_id):
        await message.reply_text(
            S.ALREADY_RUNNING,
            parse_mode=ParseMode.HTML,
        )
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


async def cmd_end_higherlower(client: Client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        return

    if not message.from_user:
        return

    chat_id = message.chat.id
    game = get_game(chat_id)

    if not game:
        await message.reply_text("❌ No Higher or Lower game is active.")
        return

    if message.from_user.id not in game["players"] and message.from_user.id != game["host_id"]:
        await message.reply_text("Only players can end this game.")
        return

    await _finish_game(client, chat_id)


async def _launch(client: Client, message: Message, chat_id: int):
    game = get_game(chat_id)

    if not game:
        return

    game["status"] = "running"
    player_count = len(game["players"])

    await message.edit_text(
        f"<blockquote>🃏 <b>HIGHER OR LOWER — STARTING!</b></blockquote>\n\n"
        f"<i>❝ {player_count} gamblers~ 10 rounds~ The deck decides everything~ ♡ ❞</i>\n\n"
        f"{format_players(game)}\n\n"
        f"<i>First card reveals in 3 seconds...</i>",
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

    await asyncio.sleep(3)

    for round_num in range(1, TOTAL_ROUNDS + 1):
        game = get_game(chat_id)

        if not game or game["status"] != "running":
            return

        if not alive_players(game):
            break

        game["round"] = round_num
        game["votes"] = {}
        game["round_open"] = True

        next_card = _draw(game)
        game["next_card"] = next_card

        curr_rank, curr_suit, _ = game["current_card"]
        board = S.scoreboard_text(game["players"])

        round_msg = await client.send_message(
            chat_id,
            S.round_text(
                round_num,
                TOTAL_ROUNDS,
                curr_rank,
                curr_suit,
                board,
                ROUND_TIMEOUT,
            ),
            reply_markup=vote_buttons(),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )

        _round_msgs[chat_id] = round_msg.id

        await asyncio.sleep(ROUND_TIMEOUT)

        game = get_game(chat_id)

        if not game or game["status"] != "running":
            return

        game["round_open"] = False

        try:
            await client.edit_message_reply_markup(
                chat_id,
                round_msg.id,
                reply_markup=None,
            )
        except Exception:
            pass

        result = resolve_round(game)

        old_card = game["current_card"]
        game["current_card"] = next_card

        curr_rank, curr_suit, _ = old_card
        next_rank, next_suit, _ = next_card

        if result["is_tie"]:
            await client.send_message(
                chat_id,
                S.tie_text(curr_rank, next_rank),
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
        else:
            await client.send_message(
                chat_id,
                S.result_text(
                    curr_rank,
                    curr_suit,
                    next_rank,
                    next_suit,
                    result["correct"],
                    result["winners"],
                    result["losers"],
                    round_num,
                    TOTAL_ROUNDS,
                ),
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )

        for ann in result["streak_announcements"]:
            if ann:
                await client.send_message(
                    chat_id,
                    ann,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )

        if "announced_dead" not in game:
            game["announced_dead"] = set()

        for uid, p in game["players"].items():
            key = (uid, round_num)

            if not p["alive"] and key not in game["announced_dead"]:
                game["announced_dead"].add(key)

                await client.send_message(
                    chat_id,
                    S.eliminated_text(p["name"], p["best_streak"]),
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )

        await asyncio.sleep(3)

    await _finish_game(client, chat_id)


async def _finish_game(client: Client, chat_id: int):
    game = get_game(chat_id)

    if not game:
        return

    game["status"] = "ended"
    players = game["players"]

    if not players:
        await client.send_message(
            chat_id,
            S.no_winner_text(),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
        end_game(chat_id)
        return

    alive = alive_players(game)
    pool = alive if alive else list(players.keys())

    winner_id = max(pool, key=lambda uid: players[uid]["points"])
    winner = players[winner_id]

    await add_win(winner_id, coins=REWARD_COINS, xp=REWARD_XP)

    for uid in players:
        if uid != winner_id:
            await add_loss(uid, xp=LOSER_XP)

    await add_group_game(chat_id, game_type="higher_lower")
    await record_game_result(
        chat_id,
        "higher_lower",
        winner_id,
        winner["name"],
        len(players),
        extra={
            "points": winner["points"],
            "best_streak": winner["best_streak"],
        },
    )

    final_board = S.scoreboard_text(players)

    await client.send_message(
        chat_id,
        S.victory_text(
            winner["name"],
            winner["points"],
            winner["best_streak"],
            final_board,
            REWARD_COINS,
            REWARD_XP,
            LOSER_XP,
        ),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

    end_game(chat_id)


async def cb_hl_join(client: Client, callback: CallbackQuery):
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
            "started": "⚡ Already started~ ♡",
            "full": S.GAME_FULL,
            "joined": S.ALREADY_JOINED,
        }
        await callback.answer(msgs.get(reason, "❌ Cannot join."), show_alert=True)
        return

    await callback.answer("🃏 Joined! Trust your instincts~ ♡")

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


async def cb_hl_start(client: Client, callback: CallbackQuery):
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

    await callback.answer("🃏 Dealing the first card~ ♡")

    game["status"] = "starting"
    await _launch(client, callback.message, chat_id)


async def cb_hl_cancel(client: Client, callback: CallbackQuery):
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


async def cb_hl_vote(client: Client, callback: CallbackQuery):
    if not callback.message:
        return

    chat_id = callback.message.chat.id
    user_id = callback.from_user.id
    game = get_game(chat_id)

    if not game or not game.get("round_open"):
        await callback.answer(S.ROUND_CLOSED, show_alert=False)
        return

    if user_id not in game["players"]:
        await callback.answer(S.NOT_IN_GAME, show_alert=True)
        return

    if not game["players"][user_id]["alive"]:
        await callback.answer(S.ALREADY_DEAD, show_alert=True)
        return

    if user_id in game["votes"]:
        await callback.answer(S.ALREADY_VOTED, show_alert=False)
        return

    choice = "higher" if "higher" in callback.data else "lower"
    game["votes"][user_id] = choice

    emoji = "⬆️" if choice == "higher" else "⬇️"

    await callback.answer(
        f"{emoji} Locked in~ ♡ Wait for the reveal.",
        show_alert=False,
    )

    try:
        await callback.message.edit_reply_markup(
            reply_markup=vote_buttons_voted(choice),
        )
    except Exception:
        pass


async def cb_hl_already(client: Client, callback: CallbackQuery):
    await callback.answer(S.ALREADY_VOTED, show_alert=False)


def register_higher_lower_handlers(app: Client):
    app.add_handler(
        MessageHandler(
            cmd_higherorlower,
            filters.command(["higherorlower", "hl", "cards"]) & filters.group,
        ),
        group=490,
    )

    app.add_handler(
        MessageHandler(
            cmd_end_higherlower,
            filters.command(["endhl", "stophl", "endhigherlower"]) & filters.group,
        ),
        group=490,
    )

    app.add_handler(CallbackQueryHandler(cb_hl_join, filters.regex("^hl_join$")), group=490)
    app.add_handler(CallbackQueryHandler(cb_hl_start, filters.regex("^hl_start$")), group=490)
    app.add_handler(CallbackQueryHandler(cb_hl_cancel, filters.regex("^hl_cancel$")), group=490)
    app.add_handler(CallbackQueryHandler(cb_hl_vote, filters.regex(r"^hl_vote_")), group=490)
    app.add_handler(CallbackQueryHandler(cb_hl_already, filters.regex("^hl_already$")), group=490)