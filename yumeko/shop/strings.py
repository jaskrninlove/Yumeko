# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
# ==========================================================

from yumeko.shop.items import TITLES, PETS, format_shop_items


def shop_home_text():
    return (
        "<blockquote>🛒 <b>Yumeko Shop</b></blockquote>\n\n"
        "<i>❝ Coins are cute, darling... but what you buy with them tells your story. ♡ ❞</i>\n\n"
        "🎖 <b>Titles</b>\n"
        "Use <code>/shop titles</code>\n\n"
        "🐾 <b>Pets</b>\n"
        "Use <code>/shop pets</code>\n\n"
        "<b>Buy:</b>\n"
        "<code>/buy title darling</code>\n"
        "<code>/buy pet fox</code>\n\n"
        "<b>Use:</b>\n"
        "<code>/use title darling</code>\n"
        "<code>/use pet fox</code>"
    )


def title_shop_text():
    return (
        "<blockquote>🎖 <b>Title Shop</b></blockquote>\n\n"
        "<i>❝ A title is not just decoration. It is your reputation. ❞</i>\n\n"
        f"{format_shop_items('title')}"
    )


def pet_shop_text():
    return (
        "<blockquote>🐾 <b>Pet Shop</b></blockquote>\n\n"
        "<i>❝ Every gambler needs a little creature watching their chaos. ♡ ❞</i>\n\n"
        f"{format_shop_items('pet')}"
    )


def buy_usage_text():
    return (
        "<blockquote>🛍 <b>Buy Usage</b></blockquote>\n\n"
        "<code>/buy title darling</code>\n"
        "<code>/buy pet puppy</code>"
    )


def use_usage_text():
    return (
        "<blockquote>🎒 <b>Use Usage</b></blockquote>\n\n"
        "<code>/use title darling</code>\n"
        "<code>/use pet puppy</code>"
    )


def item_not_found_text():
    return (
        "<blockquote>❌ <b>Item Not Found</b></blockquote>\n\n"
        "<i>❝ That item does not exist in my little shop, darling. ❞</i>"
    )


def already_owned_text(item_name: str):
    return (
        "<blockquote>🎒 <b>Already Owned</b></blockquote>\n\n"
        f"You already own <b>{item_name}</b>.\n\n"
        "<i>❝ Greedy, aren't you? ♡ ❞</i>"
    )


def not_enough_coins_text(price: int, coins: int):
    return (
        "<blockquote>💸 <b>Not Enough Coins</b></blockquote>\n\n"
        f"Price: <b>{price:,}</b>\n"
        f"Your Coins: <b>{coins:,}</b>\n\n"
        "<i>❝ Come back richer, darling. ❞</i>"
    )


def bought_text(item_name: str, price: int, rarity: str):
    return (
        "<blockquote>✅ <b>Item Purchased</b></blockquote>\n\n"
        f"Item: <b>{item_name}</b>\n"
        f"Rarity: <i>{rarity}</i>\n"
        f"Price: 💰 <b>{price:,}</b> coins\n\n"
        "<i>❝ A beautiful purchase. Yumeko approves. ♡ ❞</i>"
    )


def not_owned_text(item_name: str):
    return (
        "<blockquote>🔒 <b>Item Locked</b></blockquote>\n\n"
        f"You don't own <b>{item_name}</b> yet.\n\n"
        "<i>❝ Buy it first, darling. ❞</i>"
    )


def activated_text(item_name: str):
    return (
        "<blockquote>✨ <b>Item Activated</b></blockquote>\n\n"
        f"Active item set to <b>{item_name}</b>.\n\n"
        "<i>❝ Now you look a little more interesting. ♡ ❞</i>"
    )


def inventory_text(inv: dict):
    active_title = inv.get("active_title")
    active_pet = inv.get("active_pet")

    active_title_name = TITLES.get(active_title, {}).get("name", "None")
    active_pet_name = PETS.get(active_pet, {}).get("name", "None")

    titles = inv.get("titles", [])
    pets = inv.get("pets", [])

    owned_titles = "\n".join(
        f"◈ {TITLES[item]['name']} · <i>{TITLES[item]['rarity']}</i>"
        for item in titles if item in TITLES
    ) or "None"

    owned_pets = "\n".join(
        f"◈ {PETS[item]['name']} · <i>{PETS[item]['rarity']}</i>"
        for item in pets if item in PETS
    ) or "None"

    return (
        "<blockquote>🎒 <b>Inventory</b></blockquote>\n\n"
        f"🎖 Active Title: <b>{active_title_name}</b>\n"
        f"🐾 Active Pet: <b>{active_pet_name}</b>\n\n"
        f"<b>Owned Titles:</b>\n{owned_titles}\n\n"
        f"<b>Owned Pets:</b>\n{owned_pets}\n\n"
        "<i>❝ Your collection is your reputation. ♡ ❞</i>"
    )