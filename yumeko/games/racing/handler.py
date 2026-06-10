# ==========================================================
#  Yumeko Games Bot — Racing WebApp + Racing Duel
#  Copyright (c) 2026 Jass
# ==========================================================

import asyncio
import json
import random
import urllib.parse

from pyrogram import Client, filters
from pyrogram.enums import ChatType, ParseMode
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
)

from yumeko.config import config
from yumeko.database.users import add_user, add_win, add_loss, add_coins, add_xp


active_races = {}

FINISH = 100
RACE_TIME = 30

WIN_COINS = 70
WIN_XP = 35
LOSE_XP = 10


def mention(user_id: int, name: str):
    return f'<a href="tg://user?id={user_id}"><b>{name}</b></a>'


# ==========================================================
# WEBAPP RACING
# ==========================================================

def racing_url(chat_id: int, user_id: int) -> str:
    base = getattr(
        config,
        "RACING_WEBAPP_URL",
        "https://yumeko-racing.vercel.app",
    ).rstrip("/")

    params = urllib.parse.urlencode(
        {
            "chat": str(chat_id),
            "user": str(user_id),
        }
    )

    return f"{base}/?{params}"


def racing_webapp_button(chat_id: int, user_id: int):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🏎 Open Racing Track",
                    url=racing_url(chat_id, user_id),
                )
            ]
        ]
    )

async def race_webapp_cmd(client: Client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        await message.reply_text("🏎 Racing works best from groups.")
        return

    if not message.from_user:
        return

    await add_user(message.from_user)

    await message.reply_text(
        "<blockquote>🏎 <b>Yumeko Racing</b></blockquote>\n\n"
        "Full-screen endless racing.\n"
        "Swipe left/right, double tap for nitro, dodge traffic and collect coins.\n\n"
        "🛣 Maps change as your level rises\n"
        "🏆 Submit score after crashing\n"
        "🔥 Higher distance = better rewards\n\n"
        "<i>❝ The road never ends, darling~ ♡ ❞</i>",
        reply_markup=racing_webapp_button(message.chat.id, message.from_user.id),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


async def racing_webapp_data(client: Client, message: Message):
    data = getattr(message, "web_app_data", None)

    if not data or not message.from_user:
        return

    try:
        payload = json.loads(data.data)
    except Exception:
        return

    if payload.get("type") != "racing_score":
        return

    user_id = message.from_user.id
    score = int(payload.get("score", 0))
    coins_collected = int(payload.get("coins", 0))
    distance = int(payload.get("distance", 0))
    level = int(payload.get("level", 1))
    chat_id = int(payload.get("chat_id", 0))

    reward_coins = min(700, 25 + coins_collected * 6 + score // 180)
    reward_xp = min(300, 12 + level * 6 + distance // 110)

    await add_coins(user_id, reward_coins)
    await add_xp(user_id, reward_xp)

    text = (
        "<blockquote>🏁 <b>Racing Score Submitted</b></blockquote>\n\n"
        f"👤 <a href=\"tg://user?id={user_id}\"><b>{message.from_user.first_name}</b></a>\n"
        f"🏆 Score: <b>{score}</b>\n"
        f"🛣 Distance: <b>{distance}m</b>\n"
        f"🔥 Level: <b>{level}</b>\n"
        f"🪙 Coins Collected: <b>{coins_collected}</b>\n\n"
        "<blockquote>🎁 <b>Rewards</b></blockquote>\n\n"
        f"🪙 +<b>{reward_coins}</b> Coins\n"
        f"⭐ +<b>{reward_xp}</b> XP"
    )

    if chat_id:
        await client.send_message(chat_id, text, parse_mode=ParseMode.HTML)
    else:
        await message.reply_text(text, parse_mode=ParseMode.HTML)


# ==========================================================
# BUTTON RACING DUEL
# ==========================================================

def race_bar(pos: int, car: str):
    total = 10
    filled = min(total, max(0, pos * total // FINISH))
    empty = total - filled
    return "━" * filled + car + "·" * empty + "🏁"


def race_text(game: dict):
    p1 = game["players"][0]
    p2 = game["players"][1]

    return (
        "<blockquote>🏎 <b>Yumeko Racing Duel</b></blockquote>\n\n"
        f"🔴 {mention(p1['id'], p1['name'])}\n"
        f"{race_bar(p1['pos'], '🏎')}\n"
        f"<b>{p1['pos']}%</b>\n\n"
        f"🔵 {mention(p2['id'], p2['name'])}\n"
        f"{race_bar(p2['pos'], '🚙')}\n"
        f"<b>{p2['pos']}%</b>\n\n"
        "Tap <b>Accelerate</b> to move.\n"
        "Use <b>Nitro</b> once for a risky boost."
    )


def challenge_buttons():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("🏁 Accept Race", callback_data="race_accept")]]
    )


def race_buttons():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("⚡ Accelerate", callback_data="race_boost"),
                InlineKeyboardButton("🔥 Nitro", callback_data="race_nitro"),
            ],
            [
                InlineKeyboardButton("🛑 End Race", callback_data="race_end"),
            ],
        ]
    )


async def race_duel_cmd(client: Client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        await message.reply_text("🏎 Racing Duel can only be played in groups.")
        return

    if not message.from_user:
        return

    if not message.reply_to_message or not message.reply_to_message.from_user:
        await message.reply_text(
            "Reply to someone with <code>/raceduel</code> to challenge them.",
            parse_mode=ParseMode.HTML,
        )
        return

    challenger = message.from_user
    opponent = message.reply_to_message.from_user
    chat_id = message.chat.id

    if challenger.id == opponent.id:
        await message.reply_text("You cannot race yourself, darling~")
        return

    if chat_id in active_races:
        await message.reply_text("🏎 A race duel is already running in this group.")
        return

    await add_user(challenger)
    await add_user(opponent)

    active_races[chat_id] = {
        "status": "waiting",
        "host": challenger.id,
        "opponent": opponent.id,
        "players": [
            {
                "id": challenger.id,
                "name": challenger.first_name or "Player 1",
                "pos": 0,
                "nitro": True,
                "taps": 0,
            },
            {
                "id": opponent.id,
                "name": opponent.first_name or "Player 2",
                "pos": 0,
                "nitro": True,
                "taps": 0,
            },
        ],
        "message_id": None,
    }

    await message.reply_text(
        "<blockquote>🏎 <b>Racing Duel Challenge</b></blockquote>\n\n"
        f"{mention(challenger.id, challenger.first_name or 'Player')} challenged "
        f"{mention(opponent.id, opponent.first_name or 'Player')}!\n\n"
        "Opponent must accept to start the race.\n\n"
        "<i>❝ Engines are warm, darling~ ♡ ❞</i>",
        reply_markup=challenge_buttons(),
        parse_mode=ParseMode.HTML,
    )


async def accept_race(client: Client, callback: CallbackQuery):
    if not callback.message:
        return

    chat_id = callback.message.chat.id
    game = active_races.get(chat_id)

    if not game:
        await callback.answer("No race active.", show_alert=True)
        return

    if callback.from_user.id != game["opponent"]:
        await callback.answer("Only challenged player can accept.", show_alert=True)
        return

    game["status"] = "running"

    await callback.answer("Race started!")

    await callback.message.edit_text(
        race_text(game),
        reply_markup=race_buttons(),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

    game["message_id"] = callback.message.id
    asyncio.create_task(race_timeout(client, chat_id))


def get_player(game: dict, user_id: int):
    for p in game["players"]:
        if p["id"] == user_id:
            return p
    return None


async def boost_race(client: Client, callback: CallbackQuery):
    if not callback.message:
        return

    chat_id = callback.message.chat.id
    game = active_races.get(chat_id)

    if not game or game["status"] != "running":
        await callback.answer("No running race.", show_alert=True)
        return

    player = get_player(game, callback.from_user.id)

    if not player:
        await callback.answer("You're not in this race.", show_alert=True)
        return

    gain = random.randint(5, 10)
    player["pos"] = min(FINISH, player["pos"] + gain)
    player["taps"] += 1

    if player["pos"] >= FINISH:
        await finish_race(client, callback.message, chat_id, player)
        await callback.answer("Finished!")
        return

    await callback.answer(f"+{gain}% speed!")

    await callback.message.edit_text(
        race_text(game),
        reply_markup=race_buttons(),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


async def nitro_race(client: Client, callback: CallbackQuery):
    if not callback.message:
        return

    chat_id = callback.message.chat.id
    game = active_races.get(chat_id)

    if not game or game["status"] != "running":
        await callback.answer("No running race.", show_alert=True)
        return

    player = get_player(game, callback.from_user.id)

    if not player:
        await callback.answer("You're not in this race.", show_alert=True)
        return

    if not player["nitro"]:
        await callback.answer("Nitro already used!", show_alert=True)
        return

    player["nitro"] = False

    if random.random() <= 0.75:
        gain = random.randint(15, 28)
        player["pos"] = min(FINISH, player["pos"] + gain)
        msg = f"🔥 Nitro boost! +{gain}%"
    else:
        loss = random.randint(5, 12)
        player["pos"] = max(0, player["pos"] - loss)
        msg = f"💥 Nitro failed! -{loss}%"

    if player["pos"] >= FINISH:
        await finish_race(client, callback.message, chat_id, player)
        await callback.answer("Nitro finish!")
        return

    await callback.answer(msg)

    await callback.message.edit_text(
        race_text(game),
        reply_markup=race_buttons(),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


async def race_timeout(client: Client, chat_id: int):
    await asyncio.sleep(RACE_TIME)

    game = active_races.get(chat_id)

    if not game or game["status"] != "running":
        return

    p1, p2 = game["players"]

    if p1["pos"] == p2["pos"]:
        active_races.pop(chat_id, None)

        await client.send_message(
            chat_id,
            "<blockquote>🤝 <b>Race Draw</b></blockquote>\n\n"
            "Both racers crossed fate at the same speed~",
            parse_mode=ParseMode.HTML,
        )
        return

    winner = p1 if p1["pos"] > p2["pos"] else p2
    await finish_race_by_timeout(client, chat_id, winner)


async def finish_race(client: Client, message: Message, chat_id: int, winner: dict):
    game = active_races.get(chat_id)

    if not game:
        return

    for p in game["players"]:
        if p["id"] == winner["id"]:
            await add_win(p["id"], coins=WIN_COINS, xp=WIN_XP)
        else:
            await add_loss(p["id"], xp=LOSE_XP)

    active_races.pop(chat_id, None)

    await message.edit_text(
        race_text(game)
        + "\n\n"
        + "<blockquote>🏆 <b>Race Finished</b></blockquote>\n\n"
        + f"Winner: {mention(winner['id'], winner['name'])}\n\n"
        + f"🪙 +<b>{WIN_COINS}</b> Coins\n"
        + f"⭐ +<b>{WIN_XP}</b> XP\n"
        + f"📉 Loser: +<b>{LOSE_XP}</b> XP",
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


async def finish_race_by_timeout(client: Client, chat_id: int, winner: dict):
    game = active_races.get(chat_id)

    if not game:
        return

    for p in game["players"]:
        if p["id"] == winner["id"]:
            await add_win(p["id"], coins=WIN_COINS, xp=WIN_XP)
        else:
            await add_loss(p["id"], xp=LOSE_XP)

    active_races.pop(chat_id, None)

    await client.send_message(
        chat_id,
        race_text(game)
        + "\n\n"
        + "<blockquote>⏱ <b>Time Up!</b></blockquote>\n\n"
        + f"Winner by distance: {mention(winner['id'], winner['name'])}\n\n"
        + f"🪙 +<b>{WIN_COINS}</b> Coins\n"
        + f"⭐ +<b>{WIN_XP}</b> XP\n"
        + f"📉 Loser: +<b>{LOSE_XP}</b> XP",
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


async def end_race_callback(client: Client, callback: CallbackQuery):
    if not callback.message:
        return

    chat_id = callback.message.chat.id
    game = active_races.get(chat_id)

    if not game:
        await callback.answer("No race active.", show_alert=True)
        return

    if callback.from_user.id not in [p["id"] for p in game["players"]]:
        await callback.answer("Only racers can end this.", show_alert=True)
        return

    active_races.pop(chat_id, None)

    await callback.answer("Race ended.")
    await callback.message.edit_text(
        "<blockquote>🛑 <b>Race Ended</b></blockquote>\n\n"
        "<i>❝ Engines fade into silence~ ♡ ❞</i>",
        parse_mode=ParseMode.HTML,
    )


async def end_race_cmd(client: Client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        return

    chat_id = message.chat.id
    game = active_races.get(chat_id)

    if not game:
        await message.reply_text("No race duel is active.")
        return

    if not message.from_user:
        return

    if message.from_user.id not in [p["id"] for p in game["players"]]:
        await message.reply_text("Only racers can end this race.")
        return

    active_races.pop(chat_id, None)

    await message.reply_text(
        "<blockquote>🛑 <b>Race Ended</b></blockquote>\n\n"
        "<i>❝ Engines fade into silence~ ♡ ❞</i>",
        parse_mode=ParseMode.HTML,
    )


# ==========================================================
# REGISTER
# ==========================================================

def register_racing_handlers(app: Client):
    # /race opens WebApp
    app.add_handler(
        MessageHandler(
            race_webapp_cmd,
            filters.command(["race", "racing", "carrace"]) & filters.group,
        ),
        group=410,
    )

    # /raceduel starts old button duel
    app.add_handler(
        MessageHandler(
            race_duel_cmd,
            filters.command(["raceduel", "racebattle"]) & filters.group,
        ),
        group=410,
    )

    app.add_handler(
        MessageHandler(
            end_race_cmd,
            filters.command(["endrace", "stoprace", "endduelrace"]) & filters.group,
        ),
        group=410,
    )

    app.add_handler(
        MessageHandler(
            racing_webapp_data,
            filters.private,
        ),
        group=410,
    )

    app.add_handler(
        CallbackQueryHandler(accept_race, filters.regex("^race_accept$")),
        group=410,
    )

    app.add_handler(
        CallbackQueryHandler(boost_race, filters.regex("^race_boost$")),
        group=410,
    )

    app.add_handler(
        CallbackQueryHandler(nitro_race, filters.regex("^race_nitro$")),
        group=410,
    )

    app.add_handler(
        CallbackQueryHandler(end_race_callback, filters.regex("^race_end$")),
        group=410,
    )