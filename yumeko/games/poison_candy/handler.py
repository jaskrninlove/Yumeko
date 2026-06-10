# ==========================================================
#  Yumeko Games Bot — Poison Candy Handler
#  Copyright (c) 2026 Jass
# ==========================================================

import math

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

from yumeko.games.poison_candy import strings as S
from yumeko.games.poison_candy.game import (
    create_game,
    get_game,
    end_game,
    join_game,
    start_poison_phase,
    set_poison,
    all_poisons_set,
    begin_battle,
    pick_candy,
    current_player,
    format_players,
    board_text,
    winner_data,
    MAX_PLAYERS,
    MIN_PLAYERS,
    DEFAULT_SIZE,
)


WIN_COINS = 90
WIN_XP = 45
LOSE_XP = 12


def join_buttons():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🎮 Join Game", callback_data="pc_join")],
            [
                InlineKeyboardButton("▶️ Begin", callback_data="pc_begin"),
                InlineKeyboardButton("🛑 Cancel", callback_data="pc_cancel"),
            ],
        ]
    )


def poison_buttons(chat_id: int, size: int):
    rows = []
    total = size * size

    for r in range(size):
        row = []
        for c in range(size):
            idx = r * size + c
            row.append(
                InlineKeyboardButton(
                    "🍬",
                    callback_data=f"pc_set_{chat_id}_{idx}",
                )
            )
        rows.append(row)

    return InlineKeyboardMarkup(rows)


def candy_grid_buttons(game):
    rows = []
    size = game["size"]

    for r in range(size):
        row = []

        for c in range(size):
            idx = r * size + c
            cell = game["board"][idx]

            if cell["dead"]:
                text = "💀"
            elif cell["picked"]:
                text = "⬜"
            else:
                text = cell["emoji"]

            row.append(
                InlineKeyboardButton(
                    text,
                    callback_data=f"pc_pick_{idx}",
                )
            )

        rows.append(row)

    rows.append([InlineKeyboardButton("🛑 End Game", callback_data="pc_end")])
    return InlineKeyboardMarkup(rows)


async def send_poison_dms(client: Client, game, message: Message):
    failed = []

    for uid in game["order"]:
        player = game["players"][uid]

        try:
            await client.send_message(
                uid,
                S.dm_poison_text(
                    message.chat.title or "Group",
                    game["size"],
                ),
                reply_markup=poison_buttons(message.chat.id, game["size"]),
                parse_mode=ParseMode.HTML,
            )
        except Exception:
            failed.append(player["name"])

    return failed


def waiting_names(game):
    names = []

    for uid in game["order"]:
        if uid not in game["poisons"]:
            names.append(game["players"][uid]["name"])

    return ", ".join(names) if names else "None"


async def start_battle_if_ready(client: Client, chat_id: int):
    game = get_game(chat_id)

    if not game:
        return

    if not all_poisons_set(game):
        return

    begin_battle(chat_id)
    game = get_game(chat_id)

    current_id = current_player(game)
    current = game["players"][current_id]

    await client.send_message(
        chat_id,
        "<blockquote>⚔️ <b>BATTLE ROYALE STARTED!</b></blockquote>\n\n"
        "May the luckiest sweet tooth survive! 🍬\n\n"
        + S.battle_text(
            game,
            board_text(game),
            current["name"],
        ),
        reply_markup=candy_grid_buttons(game),
        parse_mode=ParseMode.HTML,
    )


async def cmd_poison_candy(client: Client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        await message.reply_text(
            "🍬 Poison Candy is a group multiplayer game."
        )
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


async def cmd_end_candy(client: Client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        return

    if not message.from_user:
        return

    chat_id = message.chat.id
    game = get_game(chat_id)

    if not game:
        await message.reply_text(S.NO_GAME)
        return

    if (
        message.from_user.id != game["host_id"]
        and message.from_user.id not in game["players"]
    ):
        await message.reply_text("Only players can end this candy game.")
        return

    end_game(chat_id)

    await message.reply_text(
        "<blockquote>🛑 <b>Poison Candy Ended</b></blockquote>\n\n"
        "<i>❝ The candy table closes for now~ ♡ ❞</i>",
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

    await callback.answer("🍬 Joined the candy trap~ ♡")

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


async def cb_begin(client: Client, callback: CallbackQuery):
    if not callback.message:
        return

    chat_id = callback.message.chat.id
    user = callback.from_user
    game = get_game(chat_id)

    if not game:
        await callback.answer(S.NO_GAME, show_alert=True)
        return

    if user.id != game["host_id"]:
        await callback.answer(S.HOST_ONLY, show_alert=True)
        return

    if len(game["players"]) < MIN_PLAYERS:
        await callback.answer(S.NOT_ENOUGH, show_alert=True)
        return

    start_poison_phase(chat_id, DEFAULT_SIZE)
    game = get_game(chat_id)

    failed = await send_poison_dms(client, game, callback.message)

    waiting = waiting_names(game)

    text = S.poison_phase_text(game, waiting)

    if failed:
        text += (
            "\n\n⚠️ Some players have not started the bot in DM:\n"
            + ", ".join(failed)
            + "\n\nAsk them to open the bot privately once."
        )

    await callback.answer("DM sent. Set poisons privately~ ♡")

    await callback.message.edit_text(
        text,
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


async def cb_set_poison(client: Client, callback: CallbackQuery):
    user = callback.from_user

    try:
        _, _, chat_id, cell_id = callback.data.split("_")
        chat_id = int(chat_id)
        cell_id = int(cell_id)
    except Exception:
        await callback.answer("Invalid poison.", show_alert=True)
        return

    game = get_game(chat_id)

    if not game:
        await callback.answer(S.NO_GAME, show_alert=True)
        return

    ok, reason = set_poison(chat_id, user.id, cell_id)

    if not ok:
        msgs = {
            "not_player": S.NOT_PLAYER,
            "already_set": S.POISON_ALREADY_SET,
            "not_poison_phase": "Poison phase is over.",
        }
        await callback.answer(msgs.get(reason, "Cannot set poison."), show_alert=True)
        return

    await callback.answer("🔐 Poison set!", show_alert=False)

    try:
        await callback.message.edit_text(
            S.poison_set_dm(),
            parse_mode=ParseMode.HTML,
        )
    except Exception:
        pass

    game = get_game(chat_id)
    waiting = waiting_names(game)

    await client.send_message(
        chat_id,
        f"🔐 <b>{user.first_name}</b> has set their poison. "
        f"Waiting for <b>{len(game['players']) - len(game['poisons'])}</b> more...",
        parse_mode=ParseMode.HTML,
    )

    if all_poisons_set(game):
        await start_battle_if_ready(client, chat_id)


async def cb_pick_candy(client: Client, callback: CallbackQuery):
    if not callback.message:
        return

    chat_id = callback.message.chat.id
    user = callback.from_user
    game = get_game(chat_id)

    if not game:
        await callback.answer(S.NO_GAME, show_alert=True)
        return

    try:
        cell_id = int(callback.data.replace("pc_pick_", "", 1))
    except Exception:
        await callback.answer("Invalid candy.", show_alert=True)
        return

    ok, reason, result = pick_candy(chat_id, user.id, cell_id)

    if not ok:
        msgs = {
            "not_turn": S.NOT_YOUR_TURN,
            "dead": "💀 You are already eliminated.",
            "picked": S.CELL_PICKED,
            "not_playing": "Battle has not started yet.",
        }
        await callback.answer(msgs.get(reason, "Cannot pick candy."), show_alert=True)
        return

    game = get_game(chat_id)
    player_name = game["players"][user.id]["name"]

    if result["poison"]:
        owner_id = result["poison_owner"]
        owner_name = game["players"][owner_id]["name"]

        await callback.answer("💀 Poison!", show_alert=True)

        if result["winner"]:
            winner = winner_data(game, result["winner"])

            for uid in game["players"]:
                if uid == result["winner"]:
                    await add_win(uid, coins=WIN_COINS, xp=WIN_XP)
                else:
                    await add_loss(uid, xp=LOSE_XP)

            await callback.message.edit_text(
                S.poison_pick_text(player_name, owner_name)
                + "\n\n"
                + S.winner_text(
                    winner["name"],
                    board_text(game, reveal=True),
                )
                + "\n\n"
                + f"🪙 +<b>{WIN_COINS}</b> Coins\n"
                + f"⭐ +<b>{WIN_XP}</b> XP",
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )

            end_game(chat_id)
            return

        current_id = current_player(game)
        current = game["players"][current_id]

        await callback.message.edit_text(
            S.poison_pick_text(player_name, owner_name)
            + "\n\n"
            + S.battle_text(
                game,
                board_text(game),
                current["name"],
            ),
            reply_markup=candy_grid_buttons(game),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
        return

    current_id = current_player(game)
    current = game["players"][current_id]

    await callback.answer("Safe candy~ ♡")

    await callback.message.edit_text(
        S.safe_pick_text(player_name, result["cell"]["emoji"])
        + "\n\n"
        + S.battle_text(
            game,
            board_text(game),
            current["name"],
        ),
        reply_markup=candy_grid_buttons(game),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


async def cb_end_game(client: Client, callback: CallbackQuery):
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
        "<blockquote>🛑 <b>Poison Candy Ended</b></blockquote>\n\n"
        "<i>❝ The sweetness fades into silence~ ♡ ❞</i>",
        parse_mode=ParseMode.HTML,
    )


def register_poison_candy_handlers(app: Client):
    app.add_handler(
        MessageHandler(
            cmd_poison_candy,
            filters.command(["poisoncandy", "candy"]) & filters.group,
        ),
        group=420,
    )

    app.add_handler(
        MessageHandler(
            cmd_end_candy,
            filters.command(["endcandy", "stopcandy"]) & filters.group,
        ),
        group=420,
    )

    app.add_handler(CallbackQueryHandler(cb_join, filters.regex("^pc_join$")), group=420)
    app.add_handler(CallbackQueryHandler(cb_begin, filters.regex("^pc_begin$")), group=420)
    app.add_handler(CallbackQueryHandler(cb_cancel, filters.regex("^pc_cancel$")), group=420)
    app.add_handler(CallbackQueryHandler(cb_set_poison, filters.regex(r"^pc_set_-?\d+_\d+$")), group=420)
    app.add_handler(CallbackQueryHandler(cb_pick_candy, filters.regex(r"^pc_pick_\d+$")), group=420)
    app.add_handler(CallbackQueryHandler(cb_end_game, filters.regex("^pc_end$")), group=420)