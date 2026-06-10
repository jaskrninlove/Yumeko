# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
#
#  Developer  : Jass
#  Project    : Yumeko Games Bot
#  Version    : 1.0.0
# ==========================================================

from pyrogram import filters
from pyrogram.enums import ChatType, ParseMode
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.types import Message, CallbackQuery

from yumeko.core.game_manager import (
    is_game_running,
    get_running_game,
    lock_game,
    unlock_game,
)
from yumeko.core.logger import game_started, game_finished
from yumeko.database.users import add_user
from yumeko.games.typing_race.game import (
    MIN_PLAYERS,
    create_game,
    get_game,
    end_game,
    join_game,
    start_round,
    reward_winner,
    lobby_buttons,
)
from yumeko.games.typing_race.strings import (
    lobby_text,
    started_text,
    winner_text,
    not_enough_text,
    cancelled_text,
)
from yumeko.helpers.permissions import is_admin, is_bot_admin
from yumeko.locales import get_text


async def typing_cmd(client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        await message.reply_text("Typing Race can only be played in groups.")
        return

    chat_id = message.chat.id
    user = message.from_user

    if not user:
        return

    if not await is_admin(client, chat_id, user.id):
        await message.reply_text("Only group admins can start Typing Race.")
        return

    if not await is_bot_admin(client, chat_id):
        await message.reply_text(
            "Please make me admin first, otherwise I cannot manage games properly."
        )
        return

    if is_game_running(chat_id):
        await message.reply_text(
            get_text(
                "game_already_running_global",
                game=get_running_game(chat_id),
            ),
            parse_mode=ParseMode.HTML,
        )
        return

    await add_user(user)

    create_game(chat_id, user.id, user.first_name or "Unknown")
    lock_game(chat_id, "Typing Race")

    game = get_game(chat_id)
    join_game(chat_id, user)

    game_started("Typing Race", chat_id)

    await message.reply_text(
        lobby_text(game),
        parse_mode=ParseMode.HTML,
        reply_markup=lobby_buttons(),
        disable_web_page_preview=True,
    )


async def typing_join(client, query: CallbackQuery):
    chat_id = query.message.chat.id
    user = query.from_user

    await add_user(user)

    ok, reason = join_game(chat_id, user)

    if not ok:
        if reason == "already_joined":
            await query.answer("You're already in, darling~", show_alert=True)
        elif reason == "already_started":
            await query.answer("Too late~ the race already began.", show_alert=True)
        else:
            await query.answer("No active race found.", show_alert=True)
        return

    game = get_game(chat_id)

    await query.message.edit_text(
        lobby_text(game),
        parse_mode=ParseMode.HTML,
        reply_markup=lobby_buttons(),
        disable_web_page_preview=True,
    )

    await query.answer("You joined the race!")


async def typing_start(client, query: CallbackQuery):
    chat_id = query.message.chat.id
    user = query.from_user

    game = get_game(chat_id)

    if not game:
        await query.answer("No active race found.", show_alert=True)
        return

    user_admin = await is_admin(client, chat_id, user.id)

    if user.id != game["host_id"] and not user_admin:
        await query.answer("Only host/admin can start.", show_alert=True)
        return

    if len(game["players"]) < MIN_PLAYERS:
        await query.message.edit_text(
            not_enough_text(),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
        end_game(chat_id)
        unlock_game(chat_id)
        await query.answer("Not enough players.")
        return

    sentence = start_round(chat_id)

    await query.message.edit_text(
        started_text(sentence),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

    await query.answer("Race started!")


async def typing_cancel(client, query: CallbackQuery):
    chat_id = query.message.chat.id
    user = query.from_user

    game = get_game(chat_id)

    if not game:
        await query.answer("No active race found.", show_alert=True)
        return

    user_admin = await is_admin(client, chat_id, user.id)

    if user.id != game["host_id"] and not user_admin:
        await query.answer("Only host/admin can cancel.", show_alert=True)
        return

    end_game(chat_id)
    unlock_game(chat_id)

    await query.message.edit_text(
        cancelled_text(),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

    await query.answer("Cancelled.")


async def typing_answer(client, message: Message):
    chat_id = message.chat.id
    user = message.from_user

    if not user or not message.text:
        return

    if message.text.startswith("/"):
        return

    game = get_game(chat_id)

    if not game:
        return

    if game["status"] != "running":
        return

    if user.id not in game["players"]:
        return

    if game["winner"]:
        return

    typed = message.text.strip()
    sentence = game["sentence"]

    if typed != sentence:
        return

    game["winner"] = user.id
    game["status"] = "finished"

    await reward_winner(chat_id, user.id)

    await message.reply_text(
        winner_text(user.first_name or "Unknown", sentence),
        parse_mode=ParseMode.HTML,
        reply_to_message_id=message.id,
        disable_web_page_preview=True,
    )

    game_finished("Typing Race", user.first_name or user.id)

    end_game(chat_id)
    unlock_game(chat_id)


def register_typing_race_handlers(app):
    app.add_handler(
        MessageHandler(
            typing_cmd,
            filters.command(["typingrace", "typebattle", "type"]),
        ),
        group=20,
    )

    app.add_handler(
        CallbackQueryHandler(
            typing_join,
            filters.regex("^typing_join$"),
        ),
        group=20,
    )

    app.add_handler(
        CallbackQueryHandler(
            typing_start,
            filters.regex("^typing_start$"),
        ),
        group=20,
    )

    app.add_handler(
        CallbackQueryHandler(
            typing_cancel,
            filters.regex("^typing_cancel$"),
        ),
        group=20,
    )

    app.add_handler(
        MessageHandler(
            typing_answer,
            filters.text & filters.group,
        ),
        group=-50,
    )