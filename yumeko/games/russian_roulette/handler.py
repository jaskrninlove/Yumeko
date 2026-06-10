# ==========================================================
#  Yumeko Games Bot — Russian Roulette Handler
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

from yumeko.games.russian_roulette import strings as S
from yumeko.games.russian_roulette.game import (
    create_game,
    get_game,
    end_game,
    join_game,
    start_game,
    pull_trigger,
    current_player,
    alive_players,
    format_players,
    final_scoreboard,
    force_winner,
    MIN_PLAYERS,
    MAX_PLAYERS,
    WIN_COINS,
    WIN_XP,
    LOSE_XP,
)


def lobby_buttons():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🎮 Join Game", callback_data="rr_join")],
            [
                InlineKeyboardButton("▶️ Start", callback_data="rr_start"),
                InlineKeyboardButton("🛑 Cancel", callback_data="rr_cancel"),
            ],
        ]
    )


def game_buttons():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🔫 Pull Trigger", callback_data="rr_pull")],
            [InlineKeyboardButton("🛑 End Game", callback_data="rr_end")],
        ]
    )


async def cmd_roulette(client: Client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        await message.reply_text("🔫 Russian Roulette can only be played in groups.")
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


async def cmd_rr_rules(client: Client, message: Message):
    await message.reply_text(
        S.rules_text(),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


async def cmd_end_roulette(client: Client, message: Message):
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
        await message.reply_text("Only players can end this game.")
        return

    winner_id = force_winner(game)

    if winner_id:
        winner = game["players"][winner_id]

        await add_win(winner_id, coins=WIN_COINS, xp=WIN_XP)

        for uid in game["players"]:
            if uid != winner_id:
                await add_loss(uid, xp=LOSE_XP)

        await message.reply_text(
            S.winner_text(
                winner["name"],
                final_scoreboard(game),
                WIN_COINS,
                WIN_XP,
            ),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
    else:
        await message.reply_text(
            S.no_winner_text(),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )

    end_game(chat_id)


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

    await callback.answer("🔫 Joined the table~ ♡")

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

    await callback.answer("Game started~ ♡")

    await callback.message.edit_text(
        S.arena_text(
            current["name"],
            game["round"],
            len(alive_players(game)),
        ),
        reply_markup=game_buttons(),
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
            final_scoreboard(game),
            WIN_COINS,
            WIN_XP,
        ),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

    end_game(callback.message.chat.id)


async def cb_pull(client: Client, callback: CallbackQuery):
    if not callback.message:
        return

    chat_id = callback.message.chat.id
    user = callback.from_user
    game = get_game(chat_id)

    if not game:
        await callback.answer(S.NO_GAME, show_alert=True)
        return

    ok, reason, result = pull_trigger(chat_id, user.id)

    if not ok:
        msgs = {
            "not_turn": S.NOT_YOUR_TURN,
            "dead": S.ALREADY_DEAD,
            "not_player": S.NOT_PLAYER,
            "not_playing": "Game has not started.",
        }
        await callback.answer(msgs.get(reason, "Cannot pull trigger."), show_alert=True)
        return

    game = get_game(chat_id)
    player = result["player"]

    if result["bang"]:
        await callback.answer("💥 BANG!", show_alert=True)

        if result["game_over"]:
            await finish_game(callback, game, result["winner"])
            return

        current = current_player(game)

        text = (
            S.bang_text(player["name"])
            + "\n\n"
        )

        if result["reload"]:
            text += S.reload_text() + "\n\n"

        text += S.arena_text(
            current["name"],
            game["round"],
            len(alive_players(game)),
        )

        await callback.message.edit_text(
            text,
            reply_markup=game_buttons(),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
        return

    await callback.answer("😮 Click... safe~")

    current = current_player(game)

    text = (
        S.safe_text(
            player["name"],
            result["chamber"],
        )
        + "\n\n"
    )

    if result["reload"]:
        text += S.reload_text() + "\n\n"

    text += S.arena_text(
        current["name"],
        game["round"],
        len(alive_players(game)),
    )

    await callback.message.edit_text(
        text,
        reply_markup=game_buttons(),
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

    winner_id = force_winner(game)

    await callback.answer("Game ended.")

    await finish_game(callback, game, winner_id)


def register_russian_roulette_handlers(app: Client):
    app.add_handler(
        MessageHandler(
            cmd_roulette,
            filters.command(["roulette", "rr"]) & filters.group,
        ),
        group=450,
    )

    app.add_handler(
        MessageHandler(
            cmd_end_roulette,
            filters.command(["endroulette", "stoproulette", "endrr"]) & filters.group,
        ),
        group=450,
    )

    app.add_handler(
        MessageHandler(
            cmd_rr_rules,
            filters.command(["rouletterules", "rrrules"]) & filters.group,
        ),
        group=450,
    )

    app.add_handler(CallbackQueryHandler(cb_join, filters.regex("^rr_join$")), group=450)
    app.add_handler(CallbackQueryHandler(cb_start, filters.regex("^rr_start$")), group=450)
    app.add_handler(CallbackQueryHandler(cb_cancel, filters.regex("^rr_cancel$")), group=450)
    app.add_handler(CallbackQueryHandler(cb_pull, filters.regex("^rr_pull$")), group=450)
    app.add_handler(CallbackQueryHandler(cb_end, filters.regex("^rr_end$")), group=450)