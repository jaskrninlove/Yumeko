# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
# ==========================================================

import asyncio
import html

from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.types import Message, CallbackQuery

from yumeko.database.users import add_user
from yumeko.games.rps.game import (
    RPS_TIMEOUT,
    create_game,
    get_game,
    end_game,
    set_choice,
    is_ready,
    decide_winner,
    reward_result,
    reward_draw,
    challenge_buttons,
    choice_buttons,
)
from yumeko.games.rps.strings import (
    challenge_text,
    accepted_text,
    chosen_popup,
    waiting_text,
    result_text,
    declined_text,
    timeout_text,
)


def mention(user):
    name = html.escape(user.first_name or "Player")
    return f'<a href="tg://user?id={user.id}">{name}</a>'


def get_target(message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user

    return None


async def rps_cmd(client, message: Message):
    user = message.from_user
    target = get_target(message)

    if not user:
        return

    if not target:
        await message.reply_text(
            "Reply to someone with <code>/rps</code> to challenge them, darling.",
            parse_mode=ParseMode.HTML,
            reply_to_message_id=message.id,
        )
        return

    if target.is_bot:
        await message.reply_text(
            "Yumeko refuses to gamble with bots, darling~",
            reply_to_message_id=message.id,
        )
        return

    if target.id == user.id:
        await message.reply_text(
            "Playing against yourself? How lonely~",
            reply_to_message_id=message.id,
        )
        return

    await add_user(user)
    await add_user(target)

    game_id = create_game(message.chat.id, user, target)

    await message.reply_text(
        challenge_text(mention(user), mention(target)),
        parse_mode=ParseMode.HTML,
        reply_markup=challenge_buttons(game_id),
        reply_to_message_id=message.reply_to_message.id,
        disable_web_page_preview=True,
    )

    asyncio.create_task(rps_timeout(client, message.chat.id, game_id))


async def rps_accept(client, query: CallbackQuery):
    game_id = query.data.replace("rps_accept:", "", 1)
    game = get_game(game_id)

    if not game:
        await query.answer("This duel expired, darling.", show_alert=True)
        return

    if query.from_user.id != game["target_id"]:
        await query.answer("Only the challenged player can accept.", show_alert=True)
        return

    game["status"] = "choosing"

    await query.message.edit_text(
        accepted_text(game["challenger_name"], game["target_name"]),
        parse_mode=ParseMode.HTML,
        reply_markup=choice_buttons(game_id),
        disable_web_page_preview=True,
    )

    await query.answer("Duel accepted.")


async def rps_decline(client, query: CallbackQuery):
    game_id = query.data.replace("rps_decline:", "", 1)
    game = get_game(game_id)

    if not game:
        await query.answer("This duel expired, darling.", show_alert=True)
        return

    if query.from_user.id != game["target_id"]:
        await query.answer("Only the challenged player can decline.", show_alert=True)
        return

    await query.message.edit_text(
        declined_text(game["target_name"]),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

    end_game(game_id)
    await query.answer("Declined.")


async def rps_pick(client, query: CallbackQuery):
    try:
        _, game_id, choice = query.data.split(":", 2)
    except ValueError:
        await query.answer("Invalid duel data.", show_alert=True)
        return

    game = get_game(game_id)

    if not game:
        await query.answer("This duel expired, darling.", show_alert=True)
        return

    if game["status"] != "choosing":
        await query.answer("Duel is not accepting choices.", show_alert=True)
        return

    ok, reason = set_choice(game_id, query.from_user.id, choice)

    if not ok:
        if reason == "not_player":
            await query.answer("This duel is not yours.", show_alert=True)
        elif reason == "already_chosen":
            await query.answer("You already chose, darling.", show_alert=True)
        else:
            await query.answer("Unable to choose.", show_alert=True)
        return

    await query.answer(chosen_popup())

    game = get_game(game_id)

    if not is_ready(game_id):
        try:
            await query.message.edit_text(
                waiting_text(game),
                parse_mode=ParseMode.HTML,
                reply_markup=choice_buttons(game_id),
                disable_web_page_preview=True,
            )
        except Exception as e:
            if "MESSAGE_NOT_MODIFIED" not in str(e):
                raise
        return

    result = decide_winner(game_id)

    if result["result"] == "draw":
        await reward_draw(game["challenger_id"], game["target_id"])
    else:
        await reward_result(result)

    await query.message.edit_text(
        result_text(game, result),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

    end_game(game_id)


async def rps_timeout(client, chat_id: int, game_id: str):
    await asyncio.sleep(RPS_TIMEOUT)

    game = get_game(game_id)

    if not game:
        return

    await client.send_message(
        chat_id,
        timeout_text(),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

    end_game(game_id)


def register_rps_handlers(app):
    app.add_handler(
        MessageHandler(
            rps_cmd,
            filters.command(["rps", "rockpaper", "rockpaperscissors"]),
        ),
        group=50,
    )

    app.add_handler(
        CallbackQueryHandler(rps_accept, filters.regex("^rps_accept:")),
        group=50,
    )

    app.add_handler(
        CallbackQueryHandler(rps_decline, filters.regex("^rps_decline:")),
        group=50,
    )

    app.add_handler(
        CallbackQueryHandler(rps_pick, filters.regex("^rps_pick:")),
        group=50,
    )