# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
#
#  Developer  : Jass
#  Project    : Yumeko Games Bot
#  Version    : 2.1.0
#
#  GitHub     : Private
#  License    : MIT License
#
#  This file is part of Yumeko Games Bot.
#  Unauthorized removal of this notice is discouraged.
#
#  © 2026 Jass. All Rights Reserved.
# ==========================================================

from datetime import datetime, date, timedelta

from yumeko.core.database import users_col


LEVEL_THRESHOLDS = [
    0, 100, 250, 500, 900, 1400, 2100, 3000, 4200, 5700,
    7500, 9800, 12500, 15800, 19800, 24600, 30400, 37300,
    45500, 55000, 66000, 79000, 94000, 111000, 130000,
]

RANK_TITLES = {
    1: "🌱 Seedling",
    3: "🔥 Sparked",
    5: "⚔️ Fighter",
    8: "💥 Destroyer",
    10: "🌀 Vortex",
    13: "🌩️ Thunderclap",
    16: "👁️ Phantom",
    19: "🧿 Oracle",
    22: "🏆 Legend",
    25: "👑 Yumeko",
}


def get_level(xp: int) -> int:
    level = 1
    for i, threshold in enumerate(LEVEL_THRESHOLDS):
        if xp >= threshold:
            level = i + 1
    return min(level, len(LEVEL_THRESHOLDS))


def get_rank_title(level: int) -> str:
    title = "🌱 Seedling"
    for lvl, name in RANK_TITLES.items():
        if level >= lvl:
            title = name
    return title


def xp_to_next_level(xp: int) -> int:
    level = get_level(xp)

    if level >= len(LEVEL_THRESHOLDS):
        return 0

    return LEVEL_THRESHOLDS[level] - xp


def default_user_doc(user_id: int):
    return {
        "user_id": user_id,

        "first_name": None,
        "last_name": None,
        "name": None,
        "username": None,
        "is_bot": False,

        "coins": 0,
        "xp": 0,
        "level": 1,
        "rank_title": "🌱 Seedling",

        "games_played": 0,
        "games_won": 0,
        "games_lost": 0,

        "win_streak": 0,
        "best_win_streak": 0,
        "last_game_date": None,

        "daily_streak": 0,
        "best_daily_streak": 0,
        "last_daily_claim": None,

        "commands_used": 0,
        "games_hosted": 0,

        "mafia_games": 0,
        "mafia_wins": 0,
        "mafia_losses": 0,
        "mafia_jester_wins": 0,
        "wordchain_games": 0,
        "bombparty_games": 0,
        "blackjack_games": 0,
        "reaction_games": 0,
        "typing_games": 0,

        "reaction": {
            "played": 0,
            "won": 0,
            "lost": 0,
            "best_time_ms": None,
            "avg_time_ms": None,
            "total_time_ms": 0,
            "fake_outs_dodged": 0,
            "perfect_rounds": 0,
        },

        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


async def ensure_user(user_id: int):
    user = await users_col.find_one({"user_id": user_id})

    if user:
        return user

    doc = default_user_doc(user_id)
    await users_col.insert_one(doc)
    return doc


async def add_user(user) -> bool:
    if not user:
        return False

    old = await users_col.find_one({"user_id": user.id})

    data = {
        "user_id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "name": user.first_name or "Unknown",
        "username": user.username,
        "is_bot": user.is_bot,
        "updated_at": datetime.utcnow(),
    }

    if old:
        await users_col.update_one(
            {"user_id": user.id},
            {
                "$set": data,
                "$setOnInsert": default_user_doc(user.id),
            },
            upsert=True,
        )
        return False

    doc = default_user_doc(user.id)
    doc.update(data)

    await users_col.insert_one(doc)
    return True

async def add_mafia_win(user_id: int):
    await users_col.update_one(
        {"user_id": user_id},
        {
            "$inc": {
                "mafia_games": 1,
                "mafia_wins": 1,
            }
        },
    )


async def add_mafia_loss(user_id: int):
    await users_col.update_one(
        {"user_id": user_id},
        {
            "$inc": {
                "mafia_games": 1,
                "mafia_losses": 1,
            }
        },
    )


async def add_jester_win(user_id: int):
    await users_col.update_one(
        {"user_id": user_id},
        {
            "$inc": {
                "mafia_games": 1,
                "mafia_jester_wins": 1,
            }
        },
    )

async def get_user(user_id: int):
    return await ensure_user(user_id)


async def total_users() -> int:
    return await users_col.count_documents({})


async def add_coins(user_id: int, amount: int):
    await ensure_user(user_id)

    await users_col.update_one(
        {"user_id": user_id},
        {
            "$inc": {"coins": amount},
            "$set": {"updated_at": datetime.utcnow()},
        },
        upsert=True,
    )


async def remove_coins(user_id: int, amount: int):
    await ensure_user(user_id)

    await users_col.update_one(
        {"user_id": user_id},
        {
            "$inc": {"coins": -abs(amount)},
            "$set": {"updated_at": datetime.utcnow()},
        },
        upsert=True,
    )


async def set_coins(user_id: int, amount: int):
    await ensure_user(user_id)

    await users_col.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "coins": max(0, amount),
                "updated_at": datetime.utcnow(),
            }
        },
        upsert=True,
    )


async def add_xp(user_id: int, amount: int):
    user = await ensure_user(user_id)

    current_xp = user.get("xp", 0)
    new_xp = current_xp + amount
    new_level = get_level(new_xp)
    new_rank = get_rank_title(new_level)
    old_level = get_level(current_xp)

    await users_col.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "xp": new_xp,
                "level": new_level,
                "rank_title": new_rank,
                "updated_at": datetime.utcnow(),
            }
        },
        upsert=True,
    )

    return new_level > old_level, new_level, new_rank


async def add_user(user) -> bool:
    if not user:
        return False

    old = await users_col.find_one({"user_id": user.id})

    update_data = {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "name": user.first_name or "Unknown",
        "username": user.username,
        "is_bot": user.is_bot,
        "updated_at": datetime.utcnow(),
    }

    if old:
        await users_col.update_one(
            {"user_id": user.id},
            {"$set": update_data},
        )
        return False

    doc = default_user_doc(user.id)
    doc.update(update_data)

    await users_col.insert_one(doc)
    return True

async def add_win(user_id: int, coins: int = 50, xp: int = 20):
    user = await ensure_user(user_id)

    current_xp = user.get("xp", 0)
    new_xp = current_xp + xp
    new_level = get_level(new_xp)
    old_level = get_level(current_xp)
    new_rank = get_rank_title(new_level)

    await users_col.update_one(
        {"user_id": user_id},
        {
            "$inc": {
                "games_played": 1,
                "games_won": 1,
                "coins": coins,
            },
            "$set": {
                "xp": new_xp,
                "level": new_level,
                "rank_title": new_rank,
                "updated_at": datetime.utcnow(),
            },
        },
        upsert=True,
    )

    return {
        "coins_earned": coins,
        "streak_bonus": 0,
        "new_streak": user.get("win_streak", 0),
        "leveled_up": new_level > old_level,
        "new_level": new_level,
        "rank_title": new_rank,
    }

async def add_loss(user_id: int, xp: int = 5):
    user = await ensure_user(user_id)

    today = date.today().isoformat()

    current_xp = user.get("xp", 0)
    new_xp = current_xp + xp
    new_level = get_level(new_xp)
    old_level = get_level(current_xp)
    new_rank = get_rank_title(new_level)

    await users_col.update_one(
        {"user_id": user_id},
        {
            "$inc": {
                "games_played": 1,
                "games_lost": 1,
            },
            "$set": {
                "win_streak": 0,
                "last_game_date": today,
                "xp": new_xp,
                "level": new_level,
                "rank_title": new_rank,
                "updated_at": datetime.utcnow(),
            },
        },
        upsert=True,
    )

    return {
        "leveled_up": new_level > old_level,
        "new_level": new_level,
        "rank_title": new_rank,
    }


async def increment_command(user_id: int):
    await ensure_user(user_id)

    await users_col.update_one(
        {"user_id": user_id},
        {
            "$inc": {"commands_used": 1},
            "$set": {"updated_at": datetime.utcnow()},
        },
        upsert=True,
    )


async def increment_game_hosted(user_id: int):
    await ensure_user(user_id)

    await users_col.update_one(
        {"user_id": user_id},
        {
            "$inc": {"games_hosted": 1},
            "$set": {"updated_at": datetime.utcnow()},
        },
        upsert=True,
    )


async def increment_game_counter(user_id: int, game_key: str):
    allowed = {
        "mafia": "mafia_games",
        "wordchain": "wordchain_games",
        "bombparty": "bombparty_games",
        "blackjack": "blackjack_games",
        "reaction": "reaction_games",
        "typing": "typing_games",
    }

    field = allowed.get(game_key)

    if not field:
        return

    await ensure_user(user_id)

    await users_col.update_one(
        {"user_id": user_id},
        {
            "$inc": {field: 1},
            "$set": {"updated_at": datetime.utcnow()},
        },
        upsert=True,
    )


async def claim_daily(user_id: int, coins: int = 500, xp: int = 50):
    user = await ensure_user(user_id)

    today = date.today()
    today_str = today.isoformat()

    last_claim = user.get("last_daily_claim")

    if last_claim == today_str:
        return {
            "ok": False,
            "reason": "already_claimed",
            "daily_streak": user.get("daily_streak", 0),
            "best_daily_streak": user.get("best_daily_streak", 0),
        }

    yesterday = (today - timedelta(days=1)).isoformat()

    if last_claim == yesterday:
        new_streak = user.get("daily_streak", 0) + 1
    else:
        new_streak = 1

    best = max(user.get("best_daily_streak", 0), new_streak)

    bonus = 0
    if new_streak >= 30:
        bonus = 1000
    elif new_streak >= 14:
        bonus = 500
    elif new_streak >= 7:
        bonus = 250
    elif new_streak >= 3:
        bonus = 100

    total_coins = coins + bonus

    await add_coins(user_id, total_coins)
    await add_xp(user_id, xp)

    await users_col.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "last_daily_claim": today_str,
                "daily_streak": new_streak,
                "best_daily_streak": best,
                "updated_at": datetime.utcnow(),
            }
        },
    )

    return {
        "ok": True,
        "coins": total_coins,
        "base_coins": coins,
        "bonus": bonus,
        "xp": xp,
        "daily_streak": new_streak,
        "best_daily_streak": best,
    }


async def update_reaction_time(user_id: int, time_ms: int):
    user = await ensure_user(user_id)

    reaction = user.get("reaction", {})
    old_best = reaction.get("best_time_ms")
    total_ms = reaction.get("total_time_ms", 0) + time_ms
    won_count = max(reaction.get("won", 1), 1)

    new_best = min(old_best, time_ms) if old_best else time_ms
    new_avg = total_ms // won_count

    await users_col.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "reaction.best_time_ms": new_best,
                "reaction.avg_time_ms": new_avg,
                "reaction.total_time_ms": total_ms,
                "updated_at": datetime.utcnow(),
            }
        },
    )


async def add_reaction_win(user_id: int, time_ms: int | None = None):
    await ensure_user(user_id)

    await users_col.update_one(
        {"user_id": user_id},
        {
            "$inc": {
                "reaction.played": 1,
                "reaction.won": 1,
                "reaction_games": 1,
            },
            "$set": {"updated_at": datetime.utcnow()},
        },
        upsert=True,
    )

    if time_ms is not None:
        await update_reaction_time(user_id, time_ms)


async def add_reaction_loss(user_id: int):
    await ensure_user(user_id)

    await users_col.update_one(
        {"user_id": user_id},
        {
            "$inc": {
                "reaction.played": 1,
                "reaction.lost": 1,
                "reaction_games": 1,
            },
            "$set": {"updated_at": datetime.utcnow()},
        },
        upsert=True,
    )


async def increment_fake_out_dodged(user_id: int):
    await ensure_user(user_id)

    await users_col.update_one(
        {"user_id": user_id},
        {
            "$inc": {"reaction.fake_outs_dodged": 1},
            "$set": {"updated_at": datetime.utcnow()},
        },
    )


async def increment_perfect_round(user_id: int):
    await ensure_user(user_id)

    await users_col.update_one(
        {"user_id": user_id},
        {
            "$inc": {"reaction.perfect_rounds": 1},
            "$set": {"updated_at": datetime.utcnow()},
        },
    )


async def get_leaderboard(limit: int = 10):
    cursor = users_col.find({"xp": {"$gt": 0}}).sort("xp", -1).limit(limit)
    return await cursor.to_list(length=limit)


async def get_reaction_leaderboard(limit: int = 10):
    cursor = (
        users_col.find({"reaction.best_time_ms": {"$ne": None}})
        .sort("reaction.best_time_ms", 1)
        .limit(limit)
    )
    return await cursor.to_list(length=limit)


async def get_wins_leaderboard(limit: int = 10):
    cursor = users_col.find({"games_won": {"$gt": 0}}).sort("games_won", -1).limit(limit)
    return await cursor.to_list(length=limit)


async def get_coins_leaderboard(limit: int = 10):
    cursor = users_col.find({"coins": {"$gt": 0}}).sort("coins", -1).limit(limit)
    return await cursor.to_list(length=limit)


async def get_user_rank(user_id: int) -> int:
    user = await get_user(user_id)

    if not user:
        return -1

    xp = user.get("xp", 0)
    rank = await users_col.count_documents({"xp": {"$gt": xp}})
    return rank + 1


async def ensure_user_indexes():
    try:
        await users_col.create_index("user_id", unique=True)
        await users_col.create_index("coins")
        await users_col.create_index("xp")
        await users_col.create_index("games_won")
        await users_col.create_index("level")
        await users_col.create_index("reaction.best_time_ms")
        await users_col.create_index("daily_streak")
        await users_col.create_index("best_daily_streak")
        await users_col.create_index("commands_used")
    except Exception:
        pass