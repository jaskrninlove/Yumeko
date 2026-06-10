# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
#
#  Developer  : Jass
#  Project    : Yumeko Games Bot
#  Version    : 1.0.0
# ==========================================================

import random

from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message

from yumeko.database.users import add_user
from yumeko.economy.economy_db import (
    add_coins,
    remove_coins,
    add_xp,
    get_balance,
    can_use_cooldown,
    set_cooldown,
)
from yumeko.economy.strings import (
    balance_text,
    work_text,
    crime_success_text,
    crime_fail_text,
    beg_text,
    cooldown_text,
    pay_usage_text,
    pay_success_text,
    not_enough_coins_text,
)


JOBS = [
    "Singer",
    "Artist",
    "Programmer",
    "Streamer",
    "Game Host",
    "Cafe Worker",
    "Designer",
    "Writer",
    "Voice Artist",
    "Event Manager",
]


async def balance_cmd(client, message: Message):
    user = message.from_user
    if not user:
        return

    await add_user(user)
    data = await get_balance(user.id)

    await message.reply_text(
        balance_text(user.first_name or "Player", data),
        parse_mode=ParseMode.HTML,
        reply_to_message_id=message.id,
    )


async def work_cmd(client, message: Message):
    user = message.from_user
    if not user:
        return

    await add_user(user)

    ok, remaining = await can_use_cooldown(user.id, "last_work", 1)

    if not ok:
        await message.reply_text(
            cooldown_text("work", remaining),
            parse_mode=ParseMode.HTML,
            reply_to_message_id=message.id,
        )
        return

    job = random.choice(JOBS)
    coins = random.randint(120, 350)
    xp = random.randint(10, 25)

    await add_coins(user.id, coins)
    await add_xp(user.id, xp)
    await set_cooldown(user.id, "last_work")

    await message.reply_text(
        work_text(job, coins, xp),
        parse_mode=ParseMode.HTML,
        reply_to_message_id=message.id,
    )


async def crime_cmd(client, message: Message):
    user = message.from_user
    if not user:
        return

    await add_user(user)

    ok, remaining = await can_use_cooldown(user.id, "last_crime", 2)

    if not ok:
        await message.reply_text(
            cooldown_text("crime", remaining),
            parse_mode=ParseMode.HTML,
            reply_to_message_id=message.id,
        )
        return

    success = random.randint(1, 100) <= 60
    xp = random.randint(10, 25)

    if success:
        coins = random.randint(300, 900)
        await add_coins(user.id, coins)
        await add_xp(user.id, xp)
        text = crime_success_text(coins, xp)
    else:
        balance = await get_balance(user.id)
        lost = min(balance["coins"], random.randint(100, 450))
        await remove_coins(user.id, lost)
        await add_xp(user.id, xp)
        text = crime_fail_text(lost, xp)

    await set_cooldown(user.id, "last_crime")

    await message.reply_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_to_message_id=message.id,
    )


async def beg_cmd(client, message: Message):
    user = message.from_user
    if not user:
        return

    await add_user(user)

    ok, remaining = await can_use_cooldown(user.id, "last_beg", 1)

    if not ok:
        await message.reply_text(
            cooldown_text("beg", remaining),
            parse_mode=ParseMode.HTML,
            reply_to_message_id=message.id,
        )
        return

    coins = random.randint(20, 120)
    xp = random.randint(2, 8)

    await add_coins(user.id, coins)
    await add_xp(user.id, xp)
    await set_cooldown(user.id, "last_beg")

    await message.reply_text(
        beg_text(coins, xp),
        parse_mode=ParseMode.HTML,
        reply_to_message_id=message.id,
    )


async def pay_cmd(client, message: Message):
    user = message.from_user
    target = message.reply_to_message.from_user if message.reply_to_message else None

    if not user or not target or len(message.command) < 2:
        await message.reply_text(
            pay_usage_text(),
            parse_mode=ParseMode.HTML,
            reply_to_message_id=message.id,
        )
        return

    if target.is_bot or target.id == user.id:
        await message.reply_text("Invalid target, darling~", reply_to_message_id=message.id)
        return

    try:
        amount = int(message.command[1])
    except ValueError:
        await message.reply_text(pay_usage_text(), parse_mode=ParseMode.HTML)
        return

    if amount <= 0:
        await message.reply_text(pay_usage_text(), parse_mode=ParseMode.HTML)
        return

    await add_user(user)
    await add_user(target)

    sender_balance = await get_balance(user.id)

    if sender_balance["coins"] < amount:
        await message.reply_text(
            not_enough_coins_text(),
            parse_mode=ParseMode.HTML,
            reply_to_message_id=message.id,
        )
        return

    await remove_coins(user.id, amount)
    await add_coins(target.id, amount)

    await message.reply_text(
        pay_success_text(
            user.first_name or "Player",
            target.first_name or "Player",
            amount,
        ),
        parse_mode=ParseMode.HTML,
        reply_to_message_id=message.id,
    )


def register_economy_handlers(app):
    app.add_handler(MessageHandler(balance_cmd, filters.command(["balance", "bal", "wallet"])), group=140)
    app.add_handler(MessageHandler(work_cmd, filters.command("work")), group=140)
    app.add_handler(MessageHandler(crime_cmd, filters.command("crime")), group=140)
    app.add_handler(MessageHandler(beg_cmd, filters.command("beg")), group=140)
    app.add_handler(MessageHandler(pay_cmd, filters.command("pay")), group=140)