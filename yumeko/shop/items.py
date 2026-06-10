# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
# ==========================================================

TITLES = {
    "darling": {"name": "🌸 Darling", "price": 5000, "rarity": "Common"},
    "gambler": {"name": "🎭 Gambler", "price": 10000, "rarity": "Common"},
    "risk_taker": {"name": "♠️ Risk Taker", "price": 15000, "rarity": "Rare"},
    "card_shark": {"name": "🃏 Card Shark", "price": 25000, "rarity": "Rare"},
    "high_roller": {"name": "🎰 High Roller", "price": 40000, "rarity": "Epic"},
    "mafia_lord": {"name": "🎭 Mafia Lord", "price": 60000, "rarity": "Epic"},
    "arcade_royal": {"name": "👑 Arcade Royal", "price": 100000, "rarity": "Legendary"},
    "yumeko_favorite": {"name": "💜 Yumeko's Favorite", "price": 150000, "rarity": "Mythic"},
}

PETS = {
    "puppy": {"name": "🐶 Puppy", "price": 8000, "rarity": "Common"},
    "cat": {"name": "🐱 Cat", "price": 9000, "rarity": "Common"},
    "bunny": {"name": "🐰 Bunny", "price": 12000, "rarity": "Common"},
    "fox": {"name": "🦊 Fox", "price": 25000, "rarity": "Rare"},
    "panda": {"name": "🐼 Panda", "price": 45000, "rarity": "Epic"},
    "wolf": {"name": "🐺 Moon Wolf", "price": 70000, "rarity": "Epic"},
    "dragon": {"name": "🐉 Dragon", "price": 120000, "rarity": "Legendary"},
    "phoenix": {"name": "🔥 Phoenix", "price": 180000, "rarity": "Mythic"},
}


def get_item(category: str, item_id: str):
    if category == "title":
        return TITLES.get(item_id)
    if category == "pet":
        return PETS.get(item_id)
    return None


def get_items(category: str):
    return TITLES if category == "title" else PETS


def format_shop_items(category: str):
    items = get_items(category)

    return "\n".join(
        f"◈ <code>{item_id}</code> — <b>{data['name']}</b>\n"
        f"   💰 <b>{data['price']:,}</b> coins · ✨ <i>{data['rarity']}</i>"
        for item_id, data in items.items()
    )