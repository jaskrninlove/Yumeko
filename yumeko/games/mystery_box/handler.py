# ==========================================================
#  Yumeko Games Bot — Mystery Box Royale Handler
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

from yumeko.database.users import add_user, add_win, add_loss, add_coins, add_xp
from yumeko.database.groups import add_group

from yumeko.games.mystery_box import strings as S
from yumeko.games.mystery_box.game import (
    create_game,
    get_game,
    end_game,
    join_game,
    start_game,
    open_box,
    apply_steal,
    current_player,
    format_players,
    board_text,
    final_scoreboard,
    player_summary,
    steal_targets,
    MAX_PLAYERS,
    MIN_PLAYERS,
    WIN_COINS,
    WIN_XP,
    LOSE_XP,
    BOX_EMOJI,
)


def join_buttons():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🎮 Join Game", callback_data="mb_join")],
            [
                InlineKeyboardButton("▶️ Start", callback_data="mb_start"),
                InlineKeyboardButton("🛑 Cancel", callback_data="mb_cancel"),
            ],
        ]
    )


def box_buttons(game):
    rows = []

    for r in range(4):
        row = []
        for c in range(4):
            idx = r * 4 + c
            cell = game["board"][idx]

            text = cell["revealed"] if cell["opened"] else BOX_EMOJI

            row.append(
                InlineKeyboardButton(
                    text,
                    callback_data=f"mb_open_{idx}",
                )
            )

        rows.append(row)

    rows.append([InlineKeyboardButton("🛑 End Game", callback_data="mb_end")])
    return InlineKeyboardMarkup(rows)


def steal_buttons(game, thief_id: int):
    rows = []

    for uid in steal_targets(game, thief_id):
        p = game["players"][uid]
        rows.append(
            [
                InlineKeyboardButton(
                    f"⚔️ {p['name']} — 💰{p['coins']}",
                    callback_data=f"mb_steal_{uid}",
                )
            ]
        )

    rows.append([InlineKeyboardButton("Skip Steal", callback_data="mb_steal_skip")])
    return InlineKeyboardMarkup(rows)


async def cmd_mystery_box(client: Client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        await message.reply_text("🎁 Mystery Box Royale can only be played in groups.")
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
        reply_markup=join_buttons(),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


async def cmd_box_rules(client: Client, message: Message):
    await message.reply_text(
        S.rules_text(),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


async def cmd_end_box(client: Client, message: Message):
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
        await message.reply_text("Only players can end this Mystery Box game.")
        return

    end_game(chat_id)

    await message.reply_text(
        "<blockquote>🛑 <b>Mystery Box Ended</b></blockquote>\n\n"
        "<i>❝ The boxes close their secrets for now~ ♡ ❞</i>",
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

    await callback.answer("🎁 Joined the box arena~ ♡")

    game = get_game(chat_id)

    await callback.message.edit_text(
        S.lobby_text(
            game["host_name"],
            format_players(game),
            len(game["players"]),
            MAX_PLAYERS,
        ),
        reply_markup=join_buttons(),
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

    await callback.answer("Mystery Box started~ ♡")

    await callback.message.edit_text(
        S.arena_text(
            board_text(game),
            current["name"],
            game["round"],
        ),
        reply_markup=box_buttons(game),
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
    )


async def apply_final_rewards(game, winner_id: int):
    for uid, player in game["players"].items():
        total_coins = player["coins"]
        total_xp = player["xp"]

        if uid == winner_id:
            total_coins += WIN_COINS
            total_xp += WIN_XP
            await add_win(uid, coins=total_coins, xp=total_xp)
        else:
            total_xp += LOSE_XP
            if total_coins:
                await add_coins(uid, total_coins)
            await add_loss(uid, xp=total_xp)


async def finish_game_message(callback: CallbackQuery, game, winner_id: int):
    winner = game["players"][winner_id]

    await apply_final_rewards(game, winner_id)

    await callback.message.edit_text(
        S.winner_text(
            winner["name"],
            board_text(game, reveal=True),
            final_scoreboard(game),
        )
        + "\n\n"
        + f"🏆 Winner Bonus: 🪙 +<b>{WIN_COINS}</b> · ⭐ +<b>{WIN_XP}</b>",
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

    end_game(callback.message.chat.id)


async def cb_open_box(client: Client, callback: CallbackQuery):
    if not callback.message:
        return

    chat_id = callback.message.chat.id
    user = callback.from_user
    game = get_game(chat_id)

    if not game:
        await callback.answer(S.NO_GAME, show_alert=True)
        return

    try:
        box_id = int(callback.data.replace("mb_open_", "", 1))
    except Exception:
        await callback.answer("Invalid box.", show_alert=True)
        return

    ok, reason, result = open_box(chat_id, user.id, box_id)

    if not ok:
        msgs = {
            "not_turn": S.NOT_YOUR_TURN,
            "opened": S.BOX_OPENED,
            "dead": "💀 You are already eliminated.",
            "not_player": S.NOT_PLAYER,
            "pending_steal": "⚔️ Steal target must be selected first.",
            "not_playing": "Game has not started.",
        }
        await callback.answer(msgs.get(reason, "Cannot open box."), show_alert=True)
        return

    game = get_game(chat_id)
    player = result["player"]
    reward = result["reward"]

    await callback.answer(f"{reward['emoji']} {reward['name']}")

    if result["game_over"]:
        await finish_game_message(callback, game, result["winner"])
        return

    if result["needs_steal_target"]:
        pending = game["pending_steal"]
        await callback.message.edit_text(
            S.steal_choose_text(player["name"], pending["amount"]),
            reply_markup=steal_buttons(game, user.id),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
        return

    current = current_player(game)

    if result["shield_used"]:
        prefix = S.shield_saved_text(
            player["name"],
            reward["name"],
            player_summary(player),
        )
    elif result["eliminated"]:
        prefix = S.eliminated_text(
            player["name"],
            reward["name"],
        )
    else:
        prefix = S.reward_text(
            player["name"],
            reward,
            player_summary(player),
        )

    await callback.message.edit_text(
        prefix
        + "\n\n"
        + S.arena_text(
            board_text(game),
            current["name"],
            game["round"],
        ),
        reply_markup=box_buttons(game),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


async def cb_steal(client: Client, callback: CallbackQuery):
    if not callback.message:
        return

    chat_id = callback.message.chat.id
    game = get_game(chat_id)

    if not game:
        await callback.answer(S.NO_GAME, show_alert=True)
        return

    pending = game.get("pending_steal")

    if not pending:
        await callback.answer("No steal pending.", show_alert=True)
        return

    thief_id = pending["from"]

    if callback.from_user.id != thief_id:
        await callback.answer("Only thief can choose victim.", show_alert=True)
        return

    if callback.data == "mb_steal_skip":
        game["pending_steal"] = None

        from yumeko.games.mystery_box.game import next_turn
        next_turn(game)

        current = current_player(game)

        await callback.answer("Steal skipped.")

        await callback.message.edit_text(
            S.arena_text(
                board_text(game),
                current["name"],
                game["round"],
            ),
            reply_markup=box_buttons(game),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
        return

    try:
        target_id = int(callback.data.replace("mb_steal_", "", 1))
    except Exception:
        await callback.answer("Invalid target.", show_alert=True)
        return

    ok, reason, result = apply_steal(chat_id, thief_id, target_id)

    if not ok:
        await callback.answer("Cannot steal.", show_alert=True)
        return

    game = get_game(chat_id)

    await callback.answer("Coins stolen~")

    if result["game_over"]:
        await finish_game_message(callback, game, result["winner"])
        return

    current = current_player(game)

    await callback.message.edit_text(
        S.steal_result_text(
            result["thief"]["name"],
            result["target"]["name"],
            result["amount"],
        )
        + "\n\n"
        + S.arena_text(
            board_text(game),
            current["name"],
            game["round"],
        ),
        reply_markup=box_buttons(game),
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

    await callback.answer("Game ended.")
    await callback.message.edit_text(
        "<blockquote>🛑 <b>Mystery Box Ended</b></blockquote>\n\n"
        "<i>❝ Yumeko closes the last box~ ♡ ❞</i>",
        parse_mode=ParseMode.HTML,
    )


def register_mystery_box_handlers(app: Client):
    app.add_handler(
        MessageHandler(
            cmd_mystery_box,
            filters.command(["mysterybox", "box"]) & filters.group,
        ),
        group=430,
    )

    app.add_handler(
        MessageHandler(
            cmd_end_box,
            filters.command(["endbox", "stopbox"]) & filters.group,
        ),
        group=430,
    )

    app.add_handler(
        MessageHandler(
            cmd_box_rules,
            filters.command(["boxrules", "mysteryrules"]) & filters.group,
        ),
        group=430,
    )

    app.add_handler(CallbackQueryHandler(cb_join, filters.regex("^mb_join$")), group=430)
    app.add_handler(CallbackQueryHandler(cb_start, filters.regex("^mb_start$")), group=430)
    app.add_handler(CallbackQueryHandler(cb_cancel, filters.regex("^mb_cancel$")), group=430)
    app.add_handler(CallbackQueryHandler(cb_open_box, filters.regex(r"^mb_open_\d+$")), group=430)
    app.add_handler(CallbackQueryHandler(cb_steal, filters.regex(r"^mb_steal_")), group=430)
    app.add_handler(CallbackQueryHandler(cb_end, filters.regex("^mb_end$")), group=430)