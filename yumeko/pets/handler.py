# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
#
#  Developer  : Jass
#  Project    : Yumeko Games Bot
#  Version    : 1.0.0
# ==========================================================

from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message

from yumeko.database.users import add_user
from yumeko.pets.pet_db import get_pet_profile, feed_pet
from yumeko.pets.strings import (
    no_pet_text,
    pet_profile_text,
    pet_fed_text,
    pet_cooldown_text,
)


async def pet_cmd(client, message: Message):
    user = message.from_user

    if not user:
        return

    await add_user(user)

    pet = await get_pet_profile(user.id)

    if not pet:
        await message.reply_text(
            no_pet_text(),
            parse_mode=ParseMode.HTML,
            reply_to_message_id=message.id,
            disable_web_page_preview=True,
        )
        return

    await message.reply_text(
        pet_profile_text(pet),
        parse_mode=ParseMode.HTML,
        reply_to_message_id=message.id,
        disable_web_page_preview=True,
    )


async def feed_pet_cmd(client, message: Message):
    user = message.from_user

    if not user:
        return

    await add_user(user)

    pet, status, data = await feed_pet(user.id)

    if status == "no_pet":
        await message.reply_text(
            no_pet_text(),
            parse_mode=ParseMode.HTML,
            reply_to_message_id=message.id,
        )
        return

    if status == "cooldown":
        await message.reply_text(
            pet_cooldown_text(data),
            parse_mode=ParseMode.HTML,
            reply_to_message_id=message.id,
        )
        return

    await message.reply_text(
        pet_fed_text(pet, data),
        parse_mode=ParseMode.HTML,
        reply_to_message_id=message.id,
        disable_web_page_preview=True,
    )


def register_pet_handlers(app):
    app.add_handler(
        MessageHandler(
            pet_cmd,
            filters.command(["pet", "mypet"]),
        ),
        group=170,
    )

    app.add_handler(
        MessageHandler(
            feed_pet_cmd,
            filters.command(["feedpet", "petfeed"]),
        ),
        group=170,
    )