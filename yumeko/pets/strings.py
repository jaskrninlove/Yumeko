# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
# ==========================================================

from yumeko.shop.items import PETS


def no_pet_text():
    return (
        "<blockquote>🐾 <b>No Active Pet</b></blockquote>\n\n"
        "You don't have an active pet yet.\n\n"
        "Buy and use one:\n"
        "<code>/shop pets</code>\n"
        "<code>/buy pet puppy</code>\n"
        "<code>/use pet puppy</code>\n\n"
        "<i>❝ Even gamblers need companions, darling. ♡ ❞</i>"
    )


def pet_profile_text(pet: dict):
    pet_data = PETS.get(pet["pet_id"], {"name": pet["pet_id"]})
    level = pet.get("level", 1)
    xp = pet.get("xp", 0)
    needed = level * 100

    return (
        "<blockquote>🐾 <b>Pet Profile</b></blockquote>\n\n"
        f"🐶 Pet: <b>{pet_data['name']}</b>\n"
        f"⭐ Level: <b>{level}</b>\n"
        f"✨ XP: <b>{xp}/{needed}</b>\n"
        f"🍖 Hunger: <b>{pet.get('hunger', 50)}/100</b>\n\n"
        "<i>❝ A loyal little companion watching your every gamble. ♡ ❞</i>"
    )


def pet_fed_text(pet: dict, gained_xp: int):
    pet_data = PETS.get(pet["pet_id"], {"name": pet["pet_id"]})

    return (
        "<blockquote>🍖 <b>Pet Fed</b></blockquote>\n\n"
        f"{pet_data['name']} happily ate the food.\n\n"
        f"✨ Pet XP: +<b>{gained_xp}</b>\n"
        f"⭐ Level: <b>{pet.get('level', 1)}</b>\n"
        f"🍖 Hunger: <b>{pet.get('hunger', 50)}/100</b>\n\n"
        "<i>❝ How adorable. Even Yumeko smiled a little. ♡ ❞</i>"
    )


def pet_cooldown_text(remaining: str):
    return (
        "<blockquote>⏳ <b>Pet Already Fed</b></blockquote>\n\n"
        f"Feed again in: <b>{remaining}</b>\n\n"
        "<i>❝ Don't overfeed the poor thing, darling. ♡ ❞</i>"
    )