# ==========================================================
#  Yumeko Games Bot — Number Bomb Game Logic
#  Copyright (c) 2026 Jass  |  Version 2.0.0
# ==========================================================

import asyncio
import random
from datetime import datetime

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from yumeko.database.users import add_win, add_loss
from yumeko.database.groups import add_group_game, record_game_result
from yumeko.games.number_bomb import strings as S

# ── Constants ─────────────────────────────────────────────
REWARD_COINS     = 40
REWARD_XP        = 20
LOSER_XP         = 8
MIN_PLAYERS      = 2
MAX_PLAYERS      = 20
JOIN_TIMEOUT     = 60
TURN_TIMEOUT     = 15
BOMB_RANGE_MIN   = 10
BOMB_RANGE_MAX   = 40

active_games: dict[int, dict] = {}

# ── State ─────────────────────────────────────────────────

def create_game(chat_id: int, host_id: int, host_name: str):
    active_games[chat_id] = {
        "host_id":       host_id,
        "host_name":     host_name,
        "players":       {},        # user_id → {name, alive}
        "turn_order":    [],        # list of user_ids
        "turn_index":    0,
        "current_num":   0,
        "bomb_number":   None,
        "status":        "joining",
        "started_at":    datetime.utcnow(),
        "waiting_input": False,
    }

def get_game(chat_id: int): return active_games.get(chat_id)
def end_game(chat_id: int): active_games.pop(chat_id, None)

def join_game(chat_id: int, user):
    game = get_game(chat_id)
    if not game:                            return False, "no_game"
    if game["status"] != "joining":         return False, "started"
    if len(game["players"]) >= MAX_PLAYERS: return False, "full"
    if user.id in game["players"]:          return False, "joined"
    game["players"][user.id] = {"name": user.first_name or "Unknown", "alive": True}
    return True, "ok"

def format_players(game: dict) -> str:
    icons = ["💣","🎯","⚡","🔥","💀","🌙","🎲","🃏"]
    lines = []
    for i, (uid, p) in enumerate(game["players"].items()):
        status = "💀" if not p["alive"] else icons[i % len(icons)]
        lines.append(f"  {status} <b>{p['name']}</b>")
    return "\n".join(lines) if lines else "  <i>No players yet~</i>"

def alive_players(game: dict) -> list:
    return [uid for uid, p in game["players"].items() if p["alive"]]

def current_player_id(game: dict) -> int:
    order = game["turn_order"]
    idx   = game["turn_index"] % len(order)
    return order[idx]

def advance_turn(game: dict):
    game["turn_index"] = (game["turn_index"] + 1) % len(game["turn_order"])
    # Skip dead players
    attempts = 0
    while not game["players"][current_player_id(game)]["alive"]:
        game["turn_index"] = (game["turn_index"] + 1) % len(game["turn_order"])
        attempts += 1
        if attempts > len(game["turn_order"]):
            break

def join_buttons() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💣 Join Game",  callback_data="nb_join"),
            InlineKeyboardButton("🚀 Start!",     callback_data="nb_start"),
        ],
        [InlineKeyboardButton("❌ Cancel",        callback_data="nb_cancel")],
    ])

# ── Core loop ─────────────────────────────────────────────

async def run_game(client, message, chat_id: int):
    game = get_game(chat_id)
    if not game:
        return

    # Set up turn order and bomb
    alive  = list(game["players"].keys())
    random.shuffle(alive)
    game["turn_order"]  = alive
    game["turn_index"]  = 0
    game["current_num"] = 0
    bomb_range          = random.randint(BOMB_RANGE_MIN, BOMB_RANGE_MAX)
    game["bomb_number"] = random.randint(5, bomb_range)
    game["status"]      = "running"

    await message.edit_text(
        S.game_start_text(
            player_list = format_players(game),
            count       = len(game["players"]),
            bomb_range  = f"1 – {bomb_range}",
        )
    )
    await asyncio.sleep(3)

    while True:
        game = get_game(chat_id)
        if not game or game["status"] != "running":
            return

        alive_list = alive_players(game)
        if len(alive_list) <= 1:
            break

        pid      = current_player_id(game)
        pname    = game["players"][pid]["name"]
        cur_num  = game["current_num"]

        game["waiting_input"] = True
        game["expected_pid"]  = pid
        game["expected_num"]  = cur_num + 1

        prompt_msg = await message.reply_text(
            S.turn_prompt(pname, cur_num, TURN_TIMEOUT)
        )

        # Wait for correct input (set by handler) or timeout
        for _ in range(TURN_TIMEOUT * 10):
            await asyncio.sleep(0.1)
            game = get_game(chat_id)
            if not game or game["status"] != "running":
                return
            if not game["waiting_input"]:
                break
        else:
            # Timeout — eliminate player
            game["waiting_input"] = False
            game["players"][pid]["alive"] = False
            # Rebuild turn order without dead
            game["turn_order"] = [u for u in game["turn_order"]
                                  if game["players"][u]["alive"]]
            game["turn_index"] = game["turn_index"] % max(1, len(game["turn_order"]))

            try: await prompt_msg.delete()
            except: pass

            await message.reply_text(S.timeout_elimination(pname))
            await asyncio.sleep(2)
            continue

        try: await prompt_msg.delete()
        except: pass

        # Check if bomb was triggered
        result = game.get("last_result")
        if result == "bomb":
            survivors = [game["players"][u]["name"] for u in alive_players(game)]
            await message.reply_text(
                S.explosion_text(pname, game["bomb_number"], survivors)
            )
            await asyncio.sleep(2)
            # Check if only 1 left after explosion
            if len(alive_players(game)) <= 1:
                break
        elif result == "ok":
            advance_turn(game)

        await asyncio.sleep(1)

    await finish_game(client, message, chat_id)


async def finish_game(client, message, chat_id: int):
    game = get_game(chat_id)
    if not game:
        return

    alive_list = alive_players(game)

    if not alive_list:
        await message.reply_text(S.no_winner_text())
        end_game(chat_id)
        return

    winner_id   = alive_list[0]
    winner_name = game["players"][winner_id]["name"]

    await add_win(winner_id, coins=REWARD_COINS, xp=REWARD_XP)
    for uid in game["players"]:
        if uid != winner_id:
            await add_loss(uid, xp=LOSER_XP)

    await add_group_game(chat_id, game_type="number_bomb")
    await record_game_result(chat_id, "number_bomb", winner_id, winner_name,
                             len(game["players"]))

    await message.reply_text(
        S.victory_text(winner_name, game["current_num"],
                       REWARD_COINS, REWARD_XP, LOSER_XP)
    )
    end_game(chat_id)