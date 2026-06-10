# ==========================================================
#  Yumeko Games Bot — Sports Mini Games
#  Copyright (c) 2026 Jass
# ==========================================================

import random
import asyncio

from pyrogram import Client, filters
from pyrogram.enums import ChatType, ParseMode
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from yumeko.database.users import add_user, add_win, add_loss


FOOTBALL_WIN_COINS = 35
FOOTBALL_WIN_XP = 15
BOWLING_WIN_COINS = 35
BOWLING_WIN_XP = 15

HOCKEY_WIN_COINS = 45
HOCKEY_WIN_XP = 20
BOXING_WIN_COINS = 50
BOXING_WIN_XP = 25
LOSE_XP = 5

active_hockey = {}
active_boxing = {}


def mention(user):
    return f'<a href="tg://user?id={user.id}"><b>{user.first_name}</b></a>'


# ==========================================================
# FOOTBALL / SOCCER
# ==========================================================

async def football_cmd(client: Client, message: Message):
    if not message.from_user:
        return

    await add_user(message.from_user)

    sent = await client.send_dice(
        message.chat.id,
        emoji="⚽",
        reply_to_message_id=message.id,
    )

    await asyncio.sleep(3)

    value = sent.dice.value

    # Telegram football usually has 1-5 value. Higher = better.
    if value >= 4:
        await add_win(message.from_user.id, coins=FOOTBALL_WIN_COINS, xp=FOOTBALL_WIN_XP)

        text = (
            "<blockquote>⚽ <b>GOOOAL!</b></blockquote>\n\n"
            f"{mention(message.from_user)} smashed it into the net!\n\n"
            f"🪙 +<b>{FOOTBALL_WIN_COINS}</b> Coins\n"
            f"⭐ +<b>{FOOTBALL_WIN_XP}</b> XP"
        )
    else:
        await add_loss(message.from_user.id, xp=LOSE_XP)

        text = (
            "<blockquote>🥅 <b>Saved!</b></blockquote>\n\n"
            f"{mention(message.from_user)} missed the shot.\n\n"
            f"📉 Consolation: +<b>{LOSE_XP}</b> XP"
        )

    await message.reply_text(text, parse_mode=ParseMode.HTML)


# ==========================================================
# BOWLING
# ==========================================================

async def bowling_cmd(client: Client, message: Message):
    if not message.from_user:
        return

    await add_user(message.from_user)

    sent = await client.send_dice(
        message.chat.id,
        emoji="🎳",
        reply_to_message_id=message.id,
    )

    await asyncio.sleep(3)

    value = sent.dice.value

    if value >= 5:
        await add_win(message.from_user.id, coins=BOWLING_WIN_COINS, xp=BOWLING_WIN_XP)

        text = (
            "<blockquote>🎳 <b>Strike!</b></blockquote>\n\n"
            f"{mention(message.from_user)} destroyed the pins beautifully~ ♡\n\n"
            f"🪙 +<b>{BOWLING_WIN_COINS}</b> Coins\n"
            f"⭐ +<b>{BOWLING_WIN_XP}</b> XP"
        )
    else:
        await add_loss(message.from_user.id, xp=LOSE_XP)

        text = (
            "<blockquote>🎳 <b>Close Try</b></blockquote>\n\n"
            f"{mention(message.from_user)} knocked some pins, but not enough.\n\n"
            f"📉 Consolation: +<b>{LOSE_XP}</b> XP"
        )

    await message.reply_text(text, parse_mode=ParseMode.HTML)


# ==========================================================
# HOCKEY SHOOTOUT
# ==========================================================

def hockey_buttons():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("↖️ Left", callback_data="hockey_left"),
                InlineKeyboardButton("⬆️ Center", callback_data="hockey_center"),
                InlineKeyboardButton("↗️ Right", callback_data="hockey_right"),
            ]
        ]
    )


async def hockey_cmd(client: Client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        await message.reply_text("🏒 Hockey Shootout can only be played in groups.")
        return

    if not message.from_user:
        return

    await add_user(message.from_user)

    active_hockey[message.chat.id] = {
        "player_id": message.from_user.id,
        "player_name": message.from_user.first_name,
    }

    await message.reply_text(
        "<blockquote>🏒 <b>Hockey Shootout</b></blockquote>\n\n"
        f"Player: {mention(message.from_user)}\n\n"
        "Choose your shot direction.\n"
        "If the keeper dives the same way, it's saved.\n\n"
        "<i>❝ Aim carefully, darling~ ♡ ❞</i>",
        reply_markup=hockey_buttons(),
        parse_mode=ParseMode.HTML,
    )


async def hockey_callback(client: Client, callback: CallbackQuery):
    chat_id = callback.message.chat.id
    game = active_hockey.get(chat_id)

    if not game:
        await callback.answer("No hockey shootout active.", show_alert=True)
        return

    if callback.from_user.id != game["player_id"]:
        await callback.answer("This is not your shot.", show_alert=True)
        return

    shot = callback.data.replace("hockey_", "")
    keeper = random.choice(["left", "center", "right"])

    active_hockey.pop(chat_id, None)

    if shot != keeper:
        await add_win(callback.from_user.id, coins=HOCKEY_WIN_COINS, xp=HOCKEY_WIN_XP)

        text = (
            "<blockquote>🏒 <b>GOAL!</b></blockquote>\n\n"
            f"Shot: <b>{shot.title()}</b>\n"
            f"Keeper: <b>{keeper.title()}</b>\n\n"
            f"{mention(callback.from_user)} scored through the ice~ ♡\n\n"
            f"🪙 +<b>{HOCKEY_WIN_COINS}</b> Coins\n"
            f"⭐ +<b>{HOCKEY_WIN_XP}</b> XP"
        )
    else:
        await add_loss(callback.from_user.id, xp=LOSE_XP)

        text = (
            "<blockquote>🧤 <b>Saved!</b></blockquote>\n\n"
            f"Shot: <b>{shot.title()}</b>\n"
            f"Keeper: <b>{keeper.title()}</b>\n\n"
            "The keeper read your soul.\n\n"
            f"📉 Consolation: +<b>{LOSE_XP}</b> XP"
        )

    await callback.answer("Shot taken!")
    await callback.message.edit_text(text, parse_mode=ParseMode.HTML)


# ==========================================================
# BOXING DUEL
# ==========================================================

def boxing_join_buttons():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("🥊 Accept Duel", callback_data="boxing_accept")]]
    )


def boxing_action_buttons():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("👊 Punch", callback_data="boxing_punch"),
                InlineKeyboardButton("🛡 Defend", callback_data="boxing_defend"),
                InlineKeyboardButton("💥 Power", callback_data="boxing_power"),
            ]
        ]
    )


async def boxing_cmd(client: Client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        await message.reply_text("🥊 Boxing Duel can only be played in groups.")
        return

    if not message.from_user:
        return

    if not message.reply_to_message or not message.reply_to_message.from_user:
        await message.reply_text("Reply to someone with /boxing to challenge them.")
        return

    challenger = message.from_user
    opponent = message.reply_to_message.from_user

    if challenger.id == opponent.id:
        await message.reply_text("You cannot box yourself, darling~")
        return

    await add_user(challenger)
    await add_user(opponent)

    active_boxing[message.chat.id] = {
        "challenger": challenger.id,
        "opponent": opponent.id,
        "challenger_name": challenger.first_name,
        "opponent_name": opponent.first_name,
        "hp": {
            challenger.id: 100,
            opponent.id: 100,
        },
        "turn": challenger.id,
        "round": 1,
    }

    await message.reply_text(
        "<blockquote>🥊 <b>Boxing Duel</b></blockquote>\n\n"
        f"{mention(challenger)} challenged {mention(opponent)}!\n\n"
        "Opponent must accept the duel.",
        reply_markup=boxing_join_buttons(),
        parse_mode=ParseMode.HTML,
    )


async def boxing_accept_callback(client: Client, callback: CallbackQuery):
    chat_id = callback.message.chat.id
    game = active_boxing.get(chat_id)

    if not game:
        await callback.answer("No boxing duel active.", show_alert=True)
        return

    if callback.from_user.id != game["opponent"]:
        await callback.answer("Only challenged player can accept.", show_alert=True)
        return

    await callback.answer("Duel accepted!")

    await callback.message.edit_text(
        "<blockquote>🥊 <b>Duel Started</b></blockquote>\n\n"
        f"🔴 <b>{game['challenger_name']}</b>: 100 HP\n"
        f"🔵 <b>{game['opponent_name']}</b>: 100 HP\n\n"
        f"Turn: <b>{game['challenger_name']}</b>\n\n"
        "Choose your move.",
        reply_markup=boxing_action_buttons(),
        parse_mode=ParseMode.HTML,
    )


async def boxing_action_callback(client: Client, callback: CallbackQuery):
    chat_id = callback.message.chat.id
    game = active_boxing.get(chat_id)

    if not game:
        await callback.answer("No boxing duel active.", show_alert=True)
        return

    user_id = callback.from_user.id

    if user_id != game["turn"]:
        await callback.answer("Not your turn.", show_alert=True)
        return

    action = callback.data.replace("boxing_", "")

    attacker = user_id
    defender = game["opponent"] if attacker == game["challenger"] else game["challenger"]

    attacker_name = game["challenger_name"] if attacker == game["challenger"] else game["opponent_name"]
    defender_name = game["opponent_name"] if attacker == game["challenger"] else game["challenger_name"]

    if action == "punch":
        damage = random.randint(15, 25)
        line = f"👊 <b>{attacker_name}</b> punched for <b>{damage}</b> damage."
    elif action == "power":
        if random.random() < 0.55:
            damage = random.randint(28, 42)
            line = f"💥 <b>{attacker_name}</b> landed a POWER HIT for <b>{damage}</b> damage!"
        else:
            damage = 0
            line = f"💨 <b>{attacker_name}</b> missed the power hit!"
    else:
        heal = random.randint(10, 18)
        game["hp"][attacker] = min(100, game["hp"][attacker] + heal)
        damage = 0
        line = f"🛡 <b>{attacker_name}</b> defended and recovered <b>{heal}</b> HP."

    if damage:
        game["hp"][defender] = max(0, game["hp"][defender] - damage)

    if game["hp"][defender] <= 0:
        await add_win(attacker, coins=BOXING_WIN_COINS, xp=BOXING_WIN_XP)
        await add_loss(defender, xp=LOSE_XP)

        active_boxing.pop(chat_id, None)

        await callback.answer("Knockout!")

        await callback.message.edit_text(
            "<blockquote>🏆 <b>KNOCKOUT!</b></blockquote>\n\n"
            f"{line}\n\n"
            f"🥊 Winner: <b>{attacker_name}</b>\n\n"
            f"🪙 +<b>{BOXING_WIN_COINS}</b> Coins\n"
            f"⭐ +<b>{BOXING_WIN_XP}</b> XP\n"
            f"📉 Loser: +<b>{LOSE_XP}</b> XP",
            parse_mode=ParseMode.HTML,
        )
        return

    game["turn"] = defender
    game["round"] += 1

    await callback.answer("Move used!")

    await callback.message.edit_text(
        "<blockquote>🥊 <b>Boxing Duel</b></blockquote>\n\n"
        f"{line}\n\n"
        f"🔴 <b>{game['challenger_name']}</b>: {game['hp'][game['challenger']]} HP\n"
        f"🔵 <b>{game['opponent_name']}</b>: {game['hp'][game['opponent']]} HP\n\n"
        f"Turn: <b>{defender_name}</b>",
        reply_markup=boxing_action_buttons(),
        parse_mode=ParseMode.HTML,
    )


# ==========================================================
# REGISTER
# ==========================================================

def register_sports_handlers(app: Client):
    app.add_handler(
        MessageHandler(
            football_cmd,
            filters.command(["football", "soccer", "penalty"]) & filters.group,
        ),
        group=390,
    )

    app.add_handler(
        MessageHandler(
            bowling_cmd,
            filters.command(["bowling", "bowl"]) & filters.group,
        ),
        group=390,
    )

    app.add_handler(
        MessageHandler(
            hockey_cmd,
            filters.command(["hockey", "hockeyshoot"]) & filters.group,
        ),
        group=390,
    )

    app.add_handler(
        MessageHandler(
            boxing_cmd,
            filters.command(["boxing", "box"]) & filters.group,
        ),
        group=390,
    )

    app.add_handler(
        CallbackQueryHandler(hockey_callback, filters.regex("^hockey_")),
        group=390,
    )

    app.add_handler(
        CallbackQueryHandler(boxing_accept_callback, filters.regex("^boxing_accept$")),
        group=390,
    )

    app.add_handler(
        CallbackQueryHandler(boxing_action_callback, filters.regex("^boxing_(punch|defend|power)$")),
        group=390,
    )