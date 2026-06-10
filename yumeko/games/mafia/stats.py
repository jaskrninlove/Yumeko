# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
#
#  Developer  : Jass
#  Project    : Yumeko Games Bot
#  Version    : 1.0.0
# ==========================================================

from yumeko.core.database import db


mafia_stats_col = db["mafia_stats"]


async def get_stats(user_id: int):
    stats = await mafia_stats_col.find_one({"user_id": user_id})

    if not stats:
        stats = {
            "user_id": user_id,
            "games": 0,
            "wins": 0,
            "losses": 0,
            "mafia_wins": 0,
            "village_wins": 0,
            "jester_wins": 0,
            "mvp": 0,
            "kills": 0,
            "saves": 0,
            "checks": 0,
            "votes": 0,
            "survived": 0,
        }
        await mafia_stats_col.insert_one(stats)

    return stats


async def inc_stat(user_id: int, key: str, amount: int = 1):
    await get_stats(user_id)
    await mafia_stats_col.update_one(
        {"user_id": user_id},
        {"$inc": {key: amount}},
    )


async def record_game_result(game: dict, winner: str):
    for user_id, player in game["players"].items():
        await inc_stat(user_id, "games")

        won = False

        if winner == "mafia" and player["role"] == "mafia":
            won = True
            await inc_stat(user_id, "mafia_wins")

        elif winner == "village" and player["role"] != "mafia":
            won = True
            await inc_stat(user_id, "village_wins")

        elif winner == "jester" and player["role"] == "jester":
            won = True
            await inc_stat(user_id, "jester_wins")

        if won:
            await inc_stat(user_id, "wins")
        else:
            await inc_stat(user_id, "losses")

        if player.get("alive"):
            await inc_stat(user_id, "survived")


async def record_action(user_id: int, action: str):
    allowed = {
        "kill": "kills",
        "save": "saves",
        "check": "checks",
        "vote": "votes",
    }

    key = allowed.get(action)

    if key:
        await inc_stat(user_id, key)


def calculate_mvp(game: dict):
    best_user = None
    best_score = -1

    for user_id, player in game["players"].items():
        score = 0

        if player.get("alive"):
            score += 3

        if player["role"] == "mafia":
            score += 2

        if player["role"] in ["doctor", "detective", "bodyguard"]:
            score += 2

        if player["role"] == "jester":
            score += 1

        if score > best_score:
            best_score = score
            best_user = player

    return best_user


async def give_mvp(user_id: int):
    await inc_stat(user_id, "mvp")


def mafia_stats_text(name: str, stats: dict):
    return (
        "<blockquote>🎭 <b>Mafia Stats</b></blockquote>\n\n"
        f"👤 Player: <b>{name}</b>\n\n"
        f"🎮 Games: <b>{stats.get('games', 0)}</b>\n"
        f"🏆 Wins: <b>{stats.get('wins', 0)}</b>\n"
        f"💀 Losses: <b>{stats.get('losses', 0)}</b>\n"
        f"⭐ MVP: <b>{stats.get('mvp', 0)}</b>\n\n"
        f"🔪 Mafia Wins: <b>{stats.get('mafia_wins', 0)}</b>\n"
        f"🏡 Village Wins: <b>{stats.get('village_wins', 0)}</b>\n"
        f"🤡 Jester Wins: <b>{stats.get('jester_wins', 0)}</b>\n\n"
        f"🔪 Kills: <b>{stats.get('kills', 0)}</b>\n"
        f"🩺 Saves: <b>{stats.get('saves', 0)}</b>\n"
        f"🕵️ Checks: <b>{stats.get('checks', 0)}</b>\n"
        f"🗳 Votes: <b>{stats.get('votes', 0)}</b>\n"
        f"🫀 Survived: <b>{stats.get('survived', 0)}</b>\n\n"
        "<i>❝ Every lie leaves a number behind, darling. ♡ ❞</i>"
    )


def mvp_text(player: dict):
    if not player:
        return ""

    return (
        f"\n\n<blockquote>⭐ <b>Mafia MVP</b></blockquote>\n\n"
        f"🏆 <b>{player['name']}</b> was chosen as the MVP of this match.\n\n"
        f"<i>❝ A dangerous player. Yumeko noticed. ♡ ❞</i>"
    )