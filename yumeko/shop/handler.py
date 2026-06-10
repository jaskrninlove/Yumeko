# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
# ==========================================================

from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message

from yumeko.database.users import add_user
from yumeko.achievements.utils import (
    check_shop_achievement,
    check_pet_achievement,
    check_basic_achievements,
)
from yumeko.shop.items import get_item
from yumeko.shop.shop_db import (
    get_inventory,
    user_has_item,
    add_item,
    set_active_item,
    get_user_coins,
    remove_user_coins,
)
from yumeko.shop.strings import (
    shop_home_text,
    title_shop_text,
    pet_shop_text,
    buy_usage_text,
    use_usage_text,
    item_not_found_text,
    already_owned_text,
    not_enough_coins_text,
    bought_text,
    not_owned_text,
    activated_text,
    inventory_text,
)


def normalize_category(text: str):
    text = text.lower()

    if text in ["title", "titles"]:
        return "title"

    if text in ["pet", "pets"]:
        return "pet"

    return None


async def shop_cmd(client, message: Message):
    if len(message.command) < 2:
        text = shop_home_text()
    else:
        category = normalize_category(message.command[1])

        if category == "title":
            text = title_shop_text()
        elif category == "pet":
            text = pet_shop_text()
        else:
            text = shop_home_text()

    await message.reply_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_to_message_id=message.id,
        disable_web_page_preview=True,
    )


async def buy_cmd(client, message: Message):
    user = message.from_user

    if not user:
        return

    if len(message.command) < 3:
        await message.reply_text(
            buy_usage_text(),
            parse_mode=ParseMode.HTML,
            reply_to_message_id=message.id,
        )
        return

    await add_user(user)

    category = normalize_category(message.command[1])
    item_id = message.command[2].lower()

    if not category:
        await message.reply_text(
            buy_usage_text(),
            parse_mode=ParseMode.HTML,
            reply_to_message_id=message.id,
        )
        return

    item = get_item(category, item_id)

    if not item:
        await message.reply_text(
            item_not_found_text(),
            parse_mode=ParseMode.HTML,
            reply_to_message_id=message.id,
        )
        return

    if await user_has_item(user.id, category, item_id):
        await message.reply_text(
            already_owned_text(item["name"]),
            parse_mode=ParseMode.HTML,
            reply_to_message_id=message.id,
        )
        return

    coins = await get_user_coins(user.id)
    price = item["price"]

    if coins < price:
        await message.reply_text(
            not_enough_coins_text(price, coins),
            parse_mode=ParseMode.HTML,
            reply_to_message_id=message.id,
        )
        return

    await remove_user_coins(user.id, price)
    await add_item(user.id, category, item_id)

    await message.reply_text(
        bought_text(item["name"], price, item["rarity"]),
        parse_mode=ParseMode.HTML,
        reply_to_message_id=message.id,
    )

    await check_shop_achievement(client, message.chat.id, user.id)
    await check_basic_achievements(client, message.chat.id, user.id)


async def use_cmd(client, message: Message):
    user = message.from_user

    if not user:
        return

    if len(message.command) < 3:
        await message.reply_text(
            use_usage_text(),
            parse_mode=ParseMode.HTML,
            reply_to_message_id=message.id,
        )
        return

    await add_user(user)

    category = normalize_category(message.command[1])
    item_id = message.command[2].lower()

    if not category:
        await message.reply_text(
            use_usage_text(),
            parse_mode=ParseMode.HTML,
            reply_to_message_id=message.id,
        )
        return

    item = get_item(category, item_id)

    if not item:
        await message.reply_text(
            item_not_found_text(),
            parse_mode=ParseMode.HTML,
            reply_to_message_id=message.id,
        )
        return

    if not await user_has_item(user.id, category, item_id):
        await message.reply_text(
            not_owned_text(item["name"]),
            parse_mode=ParseMode.HTML,
            reply_to_message_id=message.id,
        )
        return

    await set_active_item(user.id, category, item_id)

    await message.reply_text(
        activated_text(item["name"]),
        parse_mode=ParseMode.HTML,
        reply_to_message_id=message.id,
    )

    if category == "pet":
        await check_pet_achievement(client, message.chat.id, user.id)

    await check_basic_achievements(client, message.chat.id, user.id)


async def inventory_cmd(client, message: Message):
    user = message.from_user

    if not user:
        return

    await add_user(user)
    inv = await get_inventory(user.id)

    await message.reply_text(
        inventory_text(inv),
        parse_mode=ParseMode.HTML,
        reply_to_message_id=message.id,
        disable_web_page_preview=True,
    )


def register_shop_handlers(app):
    app.add_handler(MessageHandler(shop_cmd, filters.command("shop")), group=150)
    app.add_handler(MessageHandler(buy_cmd, filters.command("buy")), group=150)
    app.add_handler(MessageHandler(use_cmd, filters.command("use")), group=150)
    app.add_handler(
        MessageHandler(
            inventory_cmd,
            filters.command(["inventory", "inv", "bag"]),
        ),
        group=150,
    )