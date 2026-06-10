# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
#
#  Developer  : Jass
#  Project    : Yumeko Games Bot
#  Version    : 1.0.0
#
#  GitHub     : Private
#  License    : MIT License
#
#  This file is part of Yumeko Games Bot.
#  Unauthorized removal of this notice is discouraged.
#
#  © 2026 Jass. All Rights Reserved.
# ==========================================================

from yumeko.core.database import users_col, groups_col


async def get_global_stats():
    users = await users_col.count_documents({})
    groups = await groups_col.count_documents({})

    pipeline = [
        {
            "$group": {
                "_id": None,
                "games_played": {"$sum": "$games_played"},
                "games_won": {"$sum": "$games_won"},
                "games_lost": {"$sum": "$games_lost"},
                "coins": {"$sum": "$coins"},
                "xp": {"$sum": "$xp"},
            }
        }
    ]

    result = await users_col.aggregate(pipeline).to_list(length=1)

    if result:
        data = result[0]
    else:
        data = {}

    return {
        "users": users,
        "groups": groups,
        "games_played": data.get("games_played", 0),
        "games_won": data.get("games_won", 0),
        "games_lost": data.get("games_lost", 0),
        "coins": data.get("coins", 0),
        "xp": data.get("xp", 0),
    }