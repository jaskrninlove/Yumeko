# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
# ==========================================================

BADGES = {
    "first_steps": {
        "name": "🎮 First Steps",
        "desc": "Start your journey in Yumeko Arcade.",
    },
    "first_win": {
        "name": "🏆 First Victory",
        "desc": "Win your first game.",
    },
    "streak_5": {
        "name": "🔥 Hot Streak",
        "desc": "Reach a 5 win streak.",
    },
    "streak_10": {
        "name": "⚡ Unstoppable",
        "desc": "Reach a 10 win streak.",
    },
    "rich_10k": {
        "name": "💰 Rich Player",
        "desc": "Reach 10,000 coins.",
    },
    "rich_100k": {
        "name": "💎 Millionaire Aura",
        "desc": "Reach 100,000 coins.",
    },
    "level_10": {
        "name": "♠️ Risk Taker",
        "desc": "Reach level 10.",
    },
    "level_25": {
        "name": "👑 Yumeko Elite",
        "desc": "Reach level 25.",
    },
    "games_100": {
        "name": "🎲 Arcade Regular",
        "desc": "Play 100 games.",
    },
    "married_soul": {
        "name": "💍 Married Soul",
        "desc": "Get married in a group.",
    },
    "love_master": {
        "name": "💞 Love Master",
        "desc": "Reach 500 love points.",
    },
    "shopper": {
        "name": "🛒 First Purchase",
        "desc": "Buy your first shop item.",
    },
    "pet_owner": {
        "name": "🐾 Pet Owner",
        "desc": "Activate your first pet.",
    },
    "gambler": {
        "name": "🎰 Gambler",
        "desc": "Play casino-style games.",
    },
    "mafia_master": {
        "name": "🎭 Mafia Master",
        "desc": "Win 5 Mafia games.",
    },
    "reaction_king": {
        "name": "⚡ Lightning Fingers",
        "desc": "Win 10 reaction battles.",
    },
    "pet_lover": {
        "name": "🐾 Pet Lover",
        "desc": "Buy or activate your first pet.",
     },
}


def get_badge(badge_id: str):
    return BADGES.get(badge_id)


def all_badges():
    return BADGES