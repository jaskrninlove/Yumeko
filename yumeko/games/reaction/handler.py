# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
#
#  Developer  : Jass
#  Project    : Yumeko Games Bot
#  Version    : 2.0.0
#
#  GitHub     : Private
#  License    : MIT License
#
#  This file is part of Yumeko Games Bot.
#  Unauthorized removal of this notice is discouraged.
#
#  © 2026 Jass. All Rights Reserved.
# ==========================================================

import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery

from yumeko.database.users import (
    add_user,
    get_user,
    get_leaderboard,
    get_reaction_leaderboard,
    get_wins_leaderboard,
    get_user_rank,
)
from yumeko.database.groups import add_group
from yumeko.games.reaction.game import (
    active_reaction_games,
    create_reaction_game,
    get_reaction_game,
    end_reaction_game,
    join_reaction_game,
    reaction_join_buttons,
    format_players,
    format_scoreboard,
    run_reaction_series,
    handle_real_tap,
    handle_fake_tap,
    REACTION_MIN_PLAYERS,
    REACTION_JOIN_TIMEOUT,
    REACTION_MAX_ROUNDS,
    REACTION_REWARD_COINS,
    REACTION_REWARD_XP,
)
from yumeko.games.reaction import strings as S


# ── Guard ─────────────────────────────────────────────────────────────────────

def _is_group(_, __, m: Message) -> bool:
    return m.chat.type.name in ("GROUP", "SUPERGROUP")

group_filter = filters.create(_is_group)


# ── /reaction ─────────────────────────────────────────────────────────────────

async def cmd_reaction(client: Client, message: Message):
    await add_user(message.from_user)
    await add_group(message.chat)

    chat_id = message.chat.id
    user    = message.from_user

    if get_reaction_game(chat_id):
        await message.reply_text(S.ALREADY_RUNNING)
        return

    create_reaction_game(chat_id, user.id, user.first_name)
    join_reaction_game(chat_id, user)

    game = get_reaction_game(chat_id)

    msg = await message.reply_text(
        S.lobby_text(
            host_name    = user.first_name,
            player_list  = format_players(game["players"]),
            player_count = len(game["players"]),
            rounds       = REACTION_MAX_ROUNDS,
            coins        = REACTION_REWARD_COINS,
            xp           = REACTION_REWARD_XP,
            timeout      = REACTION_JOIN_TIMEOUT,
        ),
        reply_markup=reaction_join_buttons(),
    )

    # Auto-start countdown
    await asyncio.sleep(REACTION_JOIN_TIMEOUT)

    game = get_reaction_game(chat_id)
    if not game or game["status"] != "joining":
        return

    if len(game["players"]) < REACTION_MIN_PLAYERS:
        end_reaction_game(chat_id)
        await msg.edit_text(S.not_enough_players_text(REACTION_MIN_PLAYERS))
        return

    game["status"] = "starting"
    await _launch_series(client, msg, chat_id)


# ── /reactionstats ────────────────────────────────────────────────────────────

async def cmd_reaction_stats(client: Client, message: Message):
    await add_user(message.from_user)
    user_id = message.from_user.id
    user    = await get_user(user_id)

    if not user:
        await message.reply_text(S.NO_STATS_YET)
        return

    r    = user.get("reaction", {})
    rank = await get_user_rank(user_id)

    await message.reply_text(
        S.stats_text(
            name           = user.get("first_name", "Unknown"),
            global_rank    = rank,
            rank_title     = user.get("rank_title", "🌱 Seedling"),
            level          = user.get("level", 1),
            xp             = user.get("xp", 0),
            coins          = user.get("coins", 0),
            games_played   = user.get("games_played", 0),
            games_won      = user.get("games_won", 0),
            games_lost     = user.get("games_lost", 0),
            win_streak     = user.get("win_streak", 0),
            best_streak    = user.get("best_win_streak", 0),
            r_played       = r.get("played", 0),
            r_won          = r.get("won", 0),
            best_ms        = r.get("best_time_ms"),
            avg_ms         = r.get("avg_time_ms"),
            fake_dodged    = r.get("fake_outs_dodged", 0),
            perfect_series = r.get("perfect_rounds", 0),
        )
    )


# ── /leaderboard ─────────────────────────────────────────────────────────────

async def cmd_leaderboard(client: Client, message: Message):
    boards = {
        "xp":       ("✨ XP Rankings",          get_leaderboard,          "xp"),
        "wins":     ("🏆 Win Rankings",          get_wins_leaderboard,     "games_won"),
        "reaction": ("⚡ Fastest Reaction Times", get_reaction_leaderboard, "reaction"),
    }

    args = message.text.split()
    mode = args[1].lower() if len(args) > 1 else "xp"
    if mode not in boards:
        mode = "xp"

    title, fetch_fn, field = boards[mode]
    players = await fetch_fn(10)

    if not players:
        await message.reply_text(S.NO_LEADERBOARD_DATA)
        return

    medals = ["🥇", "🥈", "🥉"] + ["🔹"] * 7
    lines  = []

    for i, p in enumerate(players):
        name = p.get("first_name", "Unknown")
        if mode == "reaction":
            ms      = p.get("reaction", {}).get("best_time_ms")
            val_str = f"<code>{ms}ms</code>" if ms else "—"
        elif mode == "wins":
            val_str = f"<b>{p.get('games_won', 0)} wins</b>"
        else:
            lvl     = p.get("level", 1)
            val_str = f"<b>{p.get('xp', 0)} XP</b>  ·  Lv{lvl}"
        lines.append(f"  {medals[i]} <b>{name}</b>  —  {val_str}")

    await message.reply_text(
        S.leaderboard_header(title)
        + "\n".join(lines)
        + S.leaderboard_footer()
    )


# ── Callbacks ─────────────────────────────────────────────────────────────────

async def cb_reaction_join(client: Client, callback: CallbackQuery):
    await add_user(callback.from_user)
    chat_id = callback.message.chat.id
    user    = callback.from_user
    game    = get_reaction_game(chat_id)

    if not game:
        await callback.answer(S.NO_GAME_FOUND, show_alert=True)
        return

    ok, reason = join_reaction_game(chat_id, user)

    if not ok:
        msgs = {
            "already_started": S.ALREADY_STARTED_JOIN,
            "already_joined":  S.ALREADY_JOINED,
            "full":            S.GAME_FULL,
        }
        await callback.answer(msgs.get(reason, "❌ Can't join~"), show_alert=True)
        return

    await callback.answer("✅ You're in~  ♡  Sharpen those fingers.", show_alert=False)

    game = get_reaction_game(chat_id)
    await callback.message.edit_text(
        S.lobby_updated_text(
            host_name    = game["host_name"],
            player_list  = format_players(game["players"]),
            player_count = len(game["players"]),
            rounds       = REACTION_MAX_ROUNDS,
        ),
        reply_markup=reaction_join_buttons(),
    )


async def cb_reaction_start(client: Client, callback: CallbackQuery):
    chat_id = callback.message.chat.id
    user    = callback.from_user
    game    = get_reaction_game(chat_id)

    if not game:
        await callback.answer(S.NO_GAME_FOUND, show_alert=True)
        return
    if user.id != game["host_id"]:
        await callback.answer(S.HOST_ONLY_START, show_alert=True)
        return
    if game["status"] != "joining":
        await callback.answer("⚡ Already running~  ♡", show_alert=True)
        return
    if len(game["players"]) < REACTION_MIN_PLAYERS:
        await callback.answer(
            f"👥 Need at least {REACTION_MIN_PLAYERS} brave souls~",
            show_alert=True,
        )
        return

    await callback.answer("🚀 Let the madness begin~  ♡", show_alert=False)
    game["status"] = "starting"
    await _launch_series(client, callback.message, chat_id)


async def cb_reaction_cancel(client: Client, callback: CallbackQuery):
    chat_id = callback.message.chat.id
    user    = callback.from_user
    game    = get_reaction_game(chat_id)

    if not game:
        await callback.answer(S.NO_GAME_FOUND, show_alert=True)
        return
    if user.id != game["host_id"]:
        await callback.answer(S.HOST_ONLY_CANCEL, show_alert=True)
        return

    end_reaction_game(chat_id)
    await callback.answer("❌ Cancelled~", show_alert=False)
    await callback.message.edit_text(S.CANCELLED_TEXT)


async def cb_reaction_tap(client: Client, callback: CallbackQuery):
    chat_id = callback.message.chat.id
    user    = callback.from_user
    game    = get_reaction_game(chat_id)

    if not game:
        await callback.answer(S.tap_too_late(), show_alert=False)
        return
    if user.id not in game.get("players", {}):
        await callback.answer(S.not_in_game(), show_alert=True)
        return

    result = await handle_real_tap(user.id, user.first_name, chat_id)
    await callback.answer(result, show_alert=False)


async def cb_reaction_fake_tap(client: Client, callback: CallbackQuery):
    chat_id = callback.message.chat.id
    user    = callback.from_user
    game    = get_reaction_game(chat_id)

    if not game:
        await callback.answer(S.tap_too_late(), show_alert=False)
        return
    if user.id not in game.get("players", {}):
        await callback.answer(S.not_in_game(), show_alert=True)
        return

    taunt = await handle_fake_tap(user.id, chat_id)
    await callback.answer(taunt, show_alert=True)


# ── Series launcher ───────────────────────────────────────────────────────────

async def _launch_series(client: Client, message, chat_id: int):
    game = get_reaction_game(chat_id)
    if not game:
        return

    await message.edit_text(
        S.series_start_text(
            player_list  = format_players(game["players"]),
            player_count = len(game["players"]),
            rounds       = REACTION_MAX_ROUNDS,
        )
    )
    await asyncio.sleep(3)
    await run_reaction_series(client, message, chat_id)


# ── Registration ──────────────────────────────────────────────────────────────

def register_reaction_handlers(app: Client):
    app.on_message(filters.command("reaction")         & group_filter)(cmd_reaction)
    app.on_message(filters.command(["reactionstats", "rstats"])      )(cmd_reaction_stats)
    app.on_callback_query(filters.regex("^reaction_join$")     )(cb_reaction_join)
    app.on_callback_query(filters.regex("^reaction_start$")    )(cb_reaction_start)
    app.on_callback_query(filters.regex("^reaction_cancel$")   )(cb_reaction_cancel)
    app.on_callback_query(filters.regex("^reaction_tap$")      )(cb_reaction_tap)
    app.on_callback_query(filters.regex("^reaction_fake_tap$") )(cb_reaction_fake_tap)