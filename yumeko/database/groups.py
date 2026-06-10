# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
#
#  Developer  : Jass
#  Project    : Yumeko Games Bot
#  Version    : 2.0.0
#
#  GitHub     : Private
#  License    : MIT License
#
#  This file is part of Yumeko Games Bot.
#  Unauthorized removal of this notice is discouraged.
#
#  © 2026 Jass. All Rights Reserved.
# ==========================================================

from datetime import datetime

from yumeko.core.database import groups_col


# ── Group Registration ────────────────────────────────────────────────────────

async def add_group(chat) -> bool:
    if not chat:
        return False

    old = await groups_col.find_one({"chat_id": chat.id})

    data = {
        "chat_id": chat.id,
        "title": chat.title,
        "username": chat.username,
        "type": str(chat.type),
        "updated_at": datetime.utcnow(),
    }

    if old:
        await groups_col.update_one({"chat_id": chat.id}, {"$set": data})
        return False

    data.update({
        "games_played": 0,
        "reaction_games": 0,
        "top_winner_id": None,
        "top_winner_name": None,
        "top_winner_wins": 0,
        "game_history": [],       # last 20 game results
        "created_at": datetime.utcnow(),
    })

    await groups_col.insert_one(data)
    return True


# ── Getters ───────────────────────────────────────────────────────────────────

async def get_group(chat_id: int):
    return await groups_col.find_one({"chat_id": chat_id})


async def total_groups() -> int:
    return await groups_col.count_documents({})


# ── Game Tracking ─────────────────────────────────────────────────────────────

async def add_group_game(chat_id: int, game_type: str = "reaction"):
    await groups_col.update_one(
        {"chat_id": chat_id},
        {
            "$inc": {
                "games_played": 1,
                f"{game_type}_games": 1,
            }
        },
        upsert=True,
    )


async def record_game_result(
    chat_id: int,
    game_type: str,
    winner_id: int,
    winner_name: str,
    player_count: int,
    extra: dict = None,
):
    """
    Append a game result to the group's recent history (capped at 20).
    Also updates the group's all-time top winner.
    """
    entry = {
        "game": game_type,
        "winner_id": winner_id,
        "winner_name": winner_name,
        "players": player_count,
        "played_at": datetime.utcnow().isoformat(),
    }
    if extra:
        entry.update(extra)

    # Push to history, keep last 20
    await groups_col.update_one(
        {"chat_id": chat_id},
        {
            "$push": {
                "game_history": {
                    "$each": [entry],
                    "$slice": -20,
                }
            }
        },
        upsert=True,
    )

    # Update group's all-time top winner
    group = await get_group(chat_id)
    if group:
        history = group.get("game_history", [])
        win_counts: dict = {}
        for h in history:
            wid = h.get("winner_id")
            wname = h.get("winner_name", "Unknown")
            if wid:
                win_counts[wid] = {"count": win_counts.get(wid, {}).get("count", 0) + 1, "name": wname}

        if win_counts:
            top_id = max(win_counts, key=lambda x: win_counts[x]["count"])
            await groups_col.update_one(
                {"chat_id": chat_id},
                {"$set": {
                    "top_winner_id": top_id,
                    "top_winner_name": win_counts[top_id]["name"],
                    "top_winner_wins": win_counts[top_id]["count"],
                }},
            )


# ── Group Leaderboard ─────────────────────────────────────────────────────────

async def get_most_active_groups(limit: int = 10):
    cursor = groups_col.find({}).sort("games_played", -1).limit(limit)
    return await cursor.to_list(length=limit)