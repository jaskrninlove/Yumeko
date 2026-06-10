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
import random
import time
from datetime import datetime

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from yumeko.database.users import (
    add_win,
    add_loss,
    update_reaction_time,
    increment_fake_out_dodged,
    increment_perfect_round,
    add_reaction_win,
    add_reaction_loss
)
from yumeko.database.groups import add_group_game, record_game_result
from yumeko.games.reaction import strings as S


# ── Constants ─────────────────────────────────────────────────────────────────

REACTION_REWARD_COINS   = 50
REACTION_REWARD_XP      = 25
REACTION_LOSER_XP       = 8
REACTION_MIN_PLAYERS    = 2
REACTION_MAX_PLAYERS    = 20
REACTION_JOIN_TIMEOUT   = 60
REACTION_MAX_ROUNDS     = 3
REACTION_TAP_WINDOW     = 5.0
FAKE_OUT_BASE_CHANCE    = 0.30

# Speed tier thresholds (ms)
TIER_GODLIKE = 180
TIER_INSANE  = 300
TIER_FAST    = 500
TIER_NORMAL  = 800


# ── In-memory game state ──────────────────────────────────────────────────────

active_reaction_games: dict[int, dict] = {}


# ── Helpers ───────────────────────────────────────────────────────────────────

def speed_tier(ms: int) -> str:
    if ms <= TIER_GODLIKE: return "👁️ <b>GODLIKE</b>"
    if ms <= TIER_INSANE:  return "🔥 <b>INSANE</b>"
    if ms <= TIER_FAST:    return "⚡ <b>FAST</b>"
    if ms <= TIER_NORMAL:  return "💨 Normal"
    return "🐢 Slow"


def format_players(players: dict) -> str:
    if not players:
        return "  <i>No players yet~</i>"
    icons = ["🎴", "🃏", "🎰", "🎲", "♠️", "♥️", "♦️", "♣️"]
    lines = []
    for i, p in enumerate(players.values(), 1):
        icon = icons[(i - 1) % len(icons)]
        lines.append(f"  {icon} <b>{p['name']}</b>")
    return "\n".join(lines)


def format_scoreboard(round_wins: dict, players: dict, max_rounds: int) -> str:
    lines = []
    wins_needed = (max_rounds // 2) + 1
    for uid, player in players.items():
        w   = round_wins.get(uid, 0)
        bar = "🟥" * w + "⬜" * (max_rounds - w)
        tag = "  👑" if w >= wins_needed else ""
        lines.append(f"  {bar} <b>{player['name']}</b> — {w}W{tag}")
    return "\n".join(lines) if lines else "  <i>No scores yet~</i>"


# ── State management ──────────────────────────────────────────────────────────

def create_reaction_game(chat_id: int, host_id: int, host_name: str):
    active_reaction_games[chat_id] = {
        "host_id":       host_id,
        "host_name":     host_name,
        "players":       {},
        "status":        "joining",
        "round":         1,
        "round_wins":    {},
        "fake_out_sent": False,
        "tap_time":      None,
        "round_tapped":  False,
        "round_results": [],
        "series_log":    [],
        "started_at":    datetime.utcnow(),
    }


def get_reaction_game(chat_id: int):
    return active_reaction_games.get(chat_id)


def end_reaction_game(chat_id: int):
    active_reaction_games.pop(chat_id, None)


def join_reaction_game(chat_id: int, user):
    game = get_reaction_game(chat_id)
    if not game:
        return False, "no_game"
    if game["status"] != "joining":
        return False, "already_started"
    if len(game["players"]) >= REACTION_MAX_PLAYERS:
        return False, "full"
    if user.id in game["players"]:
        return False, "already_joined"
    game["players"][user.id] = {
        "user_id":  user.id,
        "name":     user.first_name or "Unknown",
        "username": user.username,
    }
    return True, "joined"


# ── Keyboards ─────────────────────────────────────────────────────────────────

def reaction_join_buttons() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎴 Join the Game",  callback_data="reaction_join"),
            InlineKeyboardButton("🚀 Start!",          callback_data="reaction_start"),
        ],
        [
            InlineKeyboardButton("❌ Cancel",          callback_data="reaction_cancel"),
        ],
    ])


def reaction_tap_button(real: bool = True) -> InlineKeyboardMarkup:
    label = "⚡ TAP NOW!"
    cb    = "reaction_tap" if real else "reaction_fake_tap"
    return InlineKeyboardMarkup([[InlineKeyboardButton(label, callback_data=cb)]])


# ── Core round ────────────────────────────────────────────────────────────────

async def run_reaction_round(client, message, chat_id: int):
    game = get_reaction_game(chat_id)
    if not game:
        return None

    round_num   = game["round"]
    n_players   = len(game["players"])
    fake_chance = FAKE_OUT_BASE_CHANCE + (round_num - 1) * 0.12

    game["status"]        = "waiting"
    game["round_tapped"]  = False
    game["tap_time"]      = None
    game["round_results"] = []

    await message.edit_text(S.round_intro_text(round_num, REACTION_MAX_ROUNDS, n_players))
    await asyncio.sleep(random.uniform(2.5, 6.5))

    game = get_reaction_game(chat_id)
    if not game or game["status"] != "waiting":
        return None

    # ── Fake-out ──────────────────────────────────────────────────────────────
    if random.random() < fake_chance:
        game["fake_out_sent"] = True
        await message.edit_text(
            S.fake_out_text(),
            reply_markup=reaction_tap_button(real=False),
        )
        await asyncio.sleep(random.uniform(1.5, 3.0))

        game = get_reaction_game(chat_id)
        if not game:
            return None

        await message.edit_text(S.fake_out_gone_text())
        await asyncio.sleep(random.uniform(0.8, 2.5))
    else:
        game["fake_out_sent"] = False

    game = get_reaction_game(chat_id)
    if not game:
        return None

    # ── Real tap button ───────────────────────────────────────────────────────
    game["status"]   = "tapping"
    game["tap_time"] = time.time()

    await message.edit_text(
        S.tap_now_text(round_num),
        reply_markup=reaction_tap_button(real=True),
    )

    # Wait for tap window
    deadline = time.time() + REACTION_TAP_WINDOW
    while time.time() < deadline:
        await asyncio.sleep(0.05)
        game = get_reaction_game(chat_id)
        if not game:
            return None
        if game["round_tapped"]:
            # Give a tiny window for near-simultaneous taps
            await asyncio.sleep(0.4)
            break

    game = get_reaction_game(chat_id)
    if not game:
        return None

    results = game.get("round_results", [])

    # ── Timeout ───────────────────────────────────────────────────────────────
    if not results:
        game["status"] = "waiting"
        await message.edit_text(S.round_timeout_text(round_num))
        return None

    # ── Evaluate ──────────────────────────────────────────────────────────────
    results.sort(key=lambda x: x["time_ms"])
    winner     = results[0]
    winner_id  = winner["user_id"]
    winner_ms  = winner["time_ms"]
    tier       = speed_tier(winner_ms)

    game["round_wins"][winner_id] = game["round_wins"].get(winner_id, 0) + 1
    game["series_log"].append({
        "round":       round_num,
        "winner_id":   winner_id,
        "winner_name": winner["name"],
        "time_ms":     winner_ms,
    })

    # Result lines
    medal_map = {0: "🥇", 1: "🥈", 2: "🥉"}
    result_lines = "\n".join(
        f"  {medal_map.get(i, '🔹')} <b>{r['name']}</b>  "
        f"<code>{r['time_ms']}ms</code>  {speed_tier(r['time_ms'])}"
        for i, r in enumerate(results)
    )

    await message.edit_text(
        S.round_result_text(
            round_num       = round_num,
            winner_name     = winner["name"],
            winner_ms       = winner_ms,
            tier_str        = tier,
            result_lines    = result_lines,
            scoreboard      = format_scoreboard(
                game["round_wins"], game["players"], REACTION_MAX_ROUNDS
            ),
        )
    )

    await update_reaction_time(winner_id, winner_ms)
    return winner_id


# ── Series ────────────────────────────────────────────────────────────────────

async def run_reaction_series(client, message, chat_id: int):
    game        = get_reaction_game(chat_id)
    if not game:
        return
    wins_needed = (REACTION_MAX_ROUNDS // 2) + 1

    for round_num in range(1, REACTION_MAX_ROUNDS + 1):
        game = get_reaction_game(chat_id)
        if not game:
            return
        game["round"] = round_num

        await run_reaction_round(client, message, chat_id)
        await asyncio.sleep(3)

        game = get_reaction_game(chat_id)
        if not game:
            return

        for uid, w in game["round_wins"].items():
            if w >= wins_needed:
                await finish_reaction_series(client, message, chat_id, uid)
                return

    # All rounds exhausted
    game = get_reaction_game(chat_id)
    if not game:
        return

    if not game["round_wins"]:
        await message.edit_text(S.no_winner_text())
        end_reaction_game(chat_id)
        return

    champion_id = max(game["round_wins"], key=lambda x: game["round_wins"][x])
    await finish_reaction_series(client, message, chat_id, champion_id)


# ── Series finish ─────────────────────────────────────────────────────────────

async def finish_reaction_series(client, message, chat_id: int, champion_id: int):
    game = get_reaction_game(chat_id)
    if not game:
        return

    players     = game["players"]
    champion    = players.get(champion_id, {})
    champ_name  = champion.get("name", "Unknown")
    champ_wins  = game["round_wins"].get(champion_id, 0)
    is_perfect  = champ_wins == REACTION_MAX_ROUNDS

    # Reward
    win_result = await add_win(
        champion_id,
        coins=REACTION_REWARD_COINS,
        xp=REACTION_REWARD_XP,
    )
    await add_reaction_win(champion_id)
    for uid in players:
        if uid != champion_id:
            await add_loss(uid, xp=REACTION_LOSER_XP)
            await add_reaction_loss(uid)

    if is_perfect:
        await increment_perfect_round(champion_id)

    # DB
    await add_group_game(chat_id, game_type="reaction")
    await record_game_result(
        chat_id,
        game_type    = "reaction",
        winner_id    = champion_id,
        winner_name  = champ_name,
        player_count = len(players),
        extra        = {"rounds_won": champ_wins, "perfect": is_perfect},
    )

    # Round log
    log_lines = "\n".join(
        f"  R{e['round']}: 🥇 <b>{e['winner_name']}</b>  <code>{e['time_ms']}ms</code>"
        for e in game["series_log"]
    )

    # Losers
    loser_names = [p["name"] for uid, p in players.items() if uid != champion_id]
    loser_text  = ", ".join(loser_names) if loser_names else "—"

    # Streak & level-up info
    streak_info   = ""
    level_up_info = ""
    if isinstance(win_result, dict):
        bonus = win_result.get("streak_bonus", 0)
        strk  = win_result.get("new_streak", 0)
        if bonus:
            streak_info = S.streak_bonus_text(strk, bonus)
        if win_result.get("leveled_up"):
            level_up_info = S.level_up_text(
                win_result["new_level"], win_result["rank_title"]
            )

    await message.edit_text(
        S.victory_text(
            champion_name = champ_name,
            champ_wins    = champ_wins,
            total_rounds  = REACTION_MAX_ROUNDS,
            is_perfect    = is_perfect,
            round_log     = log_lines,
            loser_text    = loser_text,
            coins         = REACTION_REWARD_COINS,
            xp            = REACTION_REWARD_XP,
            loser_xp      = REACTION_LOSER_XP,
            streak_info   = streak_info,
            level_up_info = level_up_info,
        )
    )

    end_reaction_game(chat_id)


# ── Tap handlers ──────────────────────────────────────────────────────────────

async def handle_real_tap(user_id: int, user_name: str, chat_id: int) -> str:
    game = get_reaction_game(chat_id)
    if not game or game["status"] != "tapping":
        return S.tap_too_late()

    tap_time = game.get("tap_time")
    if not tap_time:
        return "❌ Something went wrong~"

    elapsed_ms = int((time.time() - tap_time) * 1000)
    already    = any(r["user_id"] == user_id for r in game["round_results"])

    if not already:
        position = len(game["round_results"]) + 1
        game["round_results"].append({
            "user_id": user_id,
            "name":    user_name,
            "time_ms": elapsed_ms,
        })
        game["round_tapped"] = True
        return S.tap_ack(position, elapsed_ms, speed_tier(elapsed_ms))

    return S.tap_too_late()


async def handle_fake_tap(user_id: int, chat_id: int) -> str:
    await increment_fake_out_dodged(user_id)
    return S.fake_tap_taunt()