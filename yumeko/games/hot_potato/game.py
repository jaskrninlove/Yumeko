# ==========================================================
#  Yumeko Games Bot — Hot Potato Game Logic
#  Copyright (c) 2026 Jass  |  Version 2.0.0
# ==========================================================

import asyncio
import random
from datetime import datetime

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from yumeko.database.users import add_win, add_loss
from yumeko.database.groups import add_group_game, record_game_result
from yumeko.games.hot_potato import strings as S

REWARD_COINS  = 50
REWARD_XP     = 25
LOSER_XP      = 8
MIN_PLAYERS   = 3
MAX_PLAYERS   = 20
JOIN_TIMEOUT  = 60
MAX_LIVES     = 3
MIN_TIMER     = 5
MAX_TIMER     = 20

active_games: dict[int, dict] = {}


def create_game(chat_id, host_id, host_name):
    active_games[chat_id] = {
        "host_id":    host_id,
        "host_name":  host_name,
        "players":    {},
        "status":     "joining",
        "holder_id":  None,
        "pass_count": 0,
        "round":      1,
        "timer_task": None,
        "started_at": datetime.utcnow(),
    }

def get_game(chat_id): return active_games.get(chat_id)
def end_game(chat_id): active_games.pop(chat_id, None)

def join_game(chat_id, user):
    game = get_game(chat_id)
    if not game:                            return False, "no_game"
    if game["status"] != "joining":         return False, "started"
    if len(game["players"]) >= MAX_PLAYERS: return False, "full"
    if user.id in game["players"]:          return False, "joined"
    game["players"][user.id] = {
        "name":  user.first_name or "Unknown",
        "lives": MAX_LIVES,
        "alive": True,
    }
    return True, "ok"

def format_players(game):
    lines = []
    for uid, p in game["players"].items():
        lives = "❤️" * p["lives"] + "🖤" * (MAX_LIVES - p["lives"])
        tag   = "  ← 🥔" if uid == game.get("holder_id") else ""
        lines.append(f"  {lives} <b>{p['name']}</b>{tag}")
    return "\n".join(lines) if lines else "  <i>No players~</i>"

def lives_dict(game):
    return {p["name"]: p["lives"] for p in game["players"].values() if p["alive"]}

def alive_players(game):
    return [uid for uid, p in game["players"].items() if p["alive"]]

def pass_button(game) -> InlineKeyboardMarkup:
    holder = game["players"].get(game["holder_id"], {})
    label  = S.pass_button(holder.get("name", "?"))
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(label, callback_data="hp_pass")
    ]])

def join_buttons() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🥔 Join Game", callback_data="hp_join"),
            InlineKeyboardButton("🚀 Start!",    callback_data="hp_start"),
        ],
        [InlineKeyboardButton("❌ Cancel",       callback_data="hp_cancel")],
    ])


async def run_round(client, message, chat_id: int):
    """Run a single explosion round: set timer, wait, explode."""
    game = get_game(chat_id)
    if not game: return

    timer = random.randint(MIN_TIMER, MAX_TIMER)
    await asyncio.sleep(timer)

    game = get_game(chat_id)
    if not game or game["status"] != "running": return

    holder_id = game["holder_id"]
    if not holder_id: return

    player    = game["players"][holder_id]
    player["lives"] -= 1
    lives_left = player["lives"]

    await message.edit_text(
        S.explosion_text(player["name"], lives_left) + "\n\n" + format_players(game),
    )

    if lives_left <= 0:
        player["alive"] = False
        # Remove from rotation
        still_alive = alive_players(game)
        if len(still_alive) <= 1:
            return  # triggers finish

    await asyncio.sleep(2)

    # Pass potato to new random holder
    alive = alive_players(game)
    if len(alive) > 1:
        new_holder = random.choice([uid for uid in alive if uid != holder_id])
    elif alive:
        new_holder = alive[0]
    else:
        return

    game["holder_id"] = new_holder
    game["pass_count"] += 1
    holder_name = game["players"][new_holder]["name"]

    await message.edit_text(
        S.potato_holder_text(holder_name, game["pass_count"], lives_dict(game)),
        reply_markup=pass_button(game),
    )


async def run_game(client, message, chat_id: int):
    game = get_game(chat_id)
    if not game: return

    # Pick starting holder
    alive         = alive_players(game)
    game["holder_id"] = random.choice(alive)
    game["status"]    = "running"

    holder_name = game["players"][game["holder_id"]]["name"]

    await message.edit_text(
        S.potato_holder_text(holder_name, 0, lives_dict(game)),
        reply_markup=pass_button(game),
    )

    while True:
        game = get_game(chat_id)
        if not game or game["status"] != "running": return

        await run_round(client, message, chat_id)

        game = get_game(chat_id)
        if not game: return

        still_alive = alive_players(game)
        if len(still_alive) <= 1:
            break

    await finish_game(client, message, chat_id)


async def finish_game(client, message, chat_id: int):
    game = get_game(chat_id)
    if not game: return

    still_alive = alive_players(game)

    if not still_alive:
        await message.edit_text("💀 <i>Everyone got burned~  No winner~  ♡</i>")
        end_game(chat_id)
        return

    winner_id   = still_alive[0]
    winner_name = game["players"][winner_id]["name"]

    await add_win(winner_id, coins=REWARD_COINS, xp=REWARD_XP)
    for uid in game["players"]:
        if uid != winner_id:
            await add_loss(uid, xp=LOSER_XP)

    await add_group_game(chat_id, game_type="hot_potato")
    await record_game_result(chat_id, "hot_potato", winner_id, winner_name,
                             len(game["players"]))

    await message.edit_text(
        S.victory_text(winner_name, game["pass_count"], REWARD_COINS, REWARD_XP)
    )
    end_game(chat_id)