# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
# ==========================================================

import random
from datetime import datetime, timedelta

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from yumeko.database.users import (
    add_win,
    add_loss,
    add_mafia_win,
    add_mafia_loss,
    add_jester_win,
)
from yumeko.database.groups import add_group_game


active_mafia_games: dict = {}

MIN_PLAYERS = 4
MAX_PLAYERS = 20

JOIN_TIME = 45
NIGHT_TIME = 45
DISCUSSION_TIME = 60
VOTE_TIME = 45
LAST_WORDS_TIME = 30

WIN_COINS = 180
WIN_XP = 90
LOSE_XP = 25
JESTER_COINS = 300
JESTER_XP = 150

DOCTOR_SELF_SAVE_LIMIT = 2


ROLES = {
    "mafia": "🔪 Shadow Dealer",
    "godfather": "🕶 Crimson Monarch",
    "doctor": "🩺 Moon Doctor",
    "detective": "🕵️ Truth Seeker",
    "bodyguard": "🛡 Silent Guardian",
    "mayor": "👑 Crowned Voice",
    "jester": "🤡 Laughing Curse",
    "cupid": "❤️ Fate Binder",
    "vigilante": "🔫 Midnight Gunner",
    "witch": "🧙 Velvet Witch",
    "silencer": "🎭 Silence Broker",
    "trickster": "🃏 Fate Trickster",
    "medium": "👻 Grave Whisperer",
    "undertaker": "⚰️ Soul Keeper",
    "arsonist": "🔥 Flame Gambler",
    "villager": "👤 Lost Citizen",
}

DEATH_NOTES = [
    "I trusted the wrong smile.",
    "Someone lied beautifully tonight.",
    "The village slept. The shadows did not.",
    "A quiet scream disappeared into the night.",
    "Yumeko heard the fear before the blade.",
    "One chair at the table is now empty.",
]


# ──────────────────────────────────────────────
#  Game Lifecycle
# ──────────────────────────────────────────────

def create_game(chat_id: int, host_id: int, host_name: str):
    active_mafia_games[chat_id] = {
        "chat_id": chat_id,
        "host_id": host_id,
        "host_name": host_name,
        "status": "joining",
        "day": 0,

        "lobby_message_id": None,

        "players": {},
        "alive": [],
        "dead": [],
        "roles": {},
        "lovers": [],

        "night_actions": {},
        "votes": {},

        "last_doctor_save": None,
        "doctor_self_saves": {},
        # key = user_id → {"chat_id": int, "expires_at": datetime, "used": False}
        "last_words_waiting": {},

        "arsonist_marks": [],

        "created_at": datetime.utcnow(),
    }


def get_game(chat_id: int):
    return active_mafia_games.get(chat_id)


def end_game(chat_id: int):
    active_mafia_games.pop(chat_id, None)


def set_lobby_message(chat_id: int, message_id: int):
    game = get_game(chat_id)
    if game:
        game["lobby_message_id"] = message_id


def role_name(role: str) -> str:
    return ROLES.get(role, role)


# ──────────────────────────────────────────────
#  Player Management
# ──────────────────────────────────────────────

def join_game(chat_id: int, user):
    game = get_game(chat_id)

    if not game:
        return False, "no_game"
    if game["status"] != "joining":
        return False, "started"
    if user.id in game["players"]:
        return False, "joined"
    if user.id in game["dead"]:
        return False, "dead_player"
    if len(game["players"]) >= MAX_PLAYERS:
        return False, "full"

    game["players"][user.id] = {
        "id": user.id,
        "name": user.first_name or "Unknown",
        "username": user.username,
        "role": None,
        "alive": True,
        "last_words_used": False,
        "afk_warnings": 0,
        # role-specific flags
        "witch_save_used": False,
        "witch_kill_used": False,
        "trickster_used": False,
        "doctor_self_saves": 0,
    }

    game["alive"].append(user.id)
    return True, "joined"


def reset_afk(game: dict, user_id: int):
    player = game["players"].get(user_id)
    if player:
        player["afk_warnings"] = 0


def add_afk_warning(game: dict, user_id: int) -> int:
    player = game["players"].get(user_id)
    if not player:
        return 0
    player["afk_warnings"] = player.get("afk_warnings", 0) + 1
    return player["afk_warnings"]


def get_non_voters(game: dict) -> list:
    return [uid for uid in game["alive"] if uid not in game.get("votes", {})]


def get_player(game: dict, user_id: int):
    return game["players"].get(user_id)


def alive_players(game: dict) -> list:
    return [game["players"][uid] for uid in game["alive"] if uid in game["players"]]


def alive_mafia(game: dict) -> list:
    return [p for p in alive_players(game) if p["role"] in ("mafia", "godfather")]


def alive_town(game: dict) -> list:
    return [p for p in alive_players(game) if p["role"] not in ("mafia", "godfather")]


def kill_player(game: dict, user_id: int):
    """Remove a player from alive list, mark dead, open last-words window."""
    player = get_player(game, user_id)

    if not player or user_id not in game["alive"]:
        return None

    game["alive"].remove(user_id)
    game["dead"].append(user_id)
    player["alive"] = False

    # Open last-words window
    game["last_words_waiting"][user_id] = {
        "chat_id": game["chat_id"],
        "expires_at": datetime.utcnow() + timedelta(seconds=LAST_WORDS_TIME),
        "used": False,
    }

    return player


def kill_lover_if_needed(game: dict, dead_id: int):
    """If dead player had a lover, kill the lover too (heartbreak)."""
    lovers = game.get("lovers", [])
    if dead_id not in lovers:
        return None

    for lover_id in lovers:
        if lover_id != dead_id and lover_id in game["alive"]:
            return kill_player(game, lover_id)

    return None


def get_alive_role(game: dict, role: str):
    """Return user_id of the first alive player with the given role, or None."""
    for uid, player in game["players"].items():
        if player["role"] == role and player["alive"]:
            return uid
    return None


def available_targets(game: dict, actor_id: int | None = None, include_self: bool = True) -> list:
    rows = []
    for uid in game["alive"]:
        if not include_self and actor_id == uid:
            continue
        player = game["players"].get(uid)
        if player:
            rows.append(player)
    return rows


# ──────────────────────────────────────────────
#  Role Assignment
# ──────────────────────────────────────────────

def build_roles(count: int) -> list:
    roles = []

    mafia_count = 1
    if count >= 7:
        mafia_count = 2
    if count >= 11:
        mafia_count = 3
    if count >= 16:
        mafia_count = 4

    roles.append("godfather")
    roles.extend(["mafia"] * max(0, mafia_count - 1))

    if count >= 4:
        roles.append("doctor")
    if count >= 5:
        roles.append("detective")
    if count >= 6:
        roles.append("jester")
    if count >= 7:
        roles.append("bodyguard")
    if count >= 8:
        roles.append("mayor")
    if count >= 9:
        roles.append("cupid")
    if count >= 10:
        roles.append("vigilante")
    if count >= 11:
        roles.append("silencer")
    if count >= 12:
        roles.append("witch")
    if count >= 13:
        roles.append("trickster")
    if count >= 14:
        roles.append("medium")
    if count >= 15:
        roles.append("undertaker")
    if count >= 16:
        roles.append("arsonist")

    while len(roles) < count:
        roles.append("villager")

    random.shuffle(roles)
    return roles


def assign_roles(chat_id: int):
    game = get_game(chat_id)
    if not game:
        return None

    user_ids = list(game["players"].keys())
    roles = build_roles(len(user_ids))

    for user_id, role in zip(user_ids, roles):
        game["players"][user_id]["role"] = role
        game["roles"][user_id] = role

    game["status"] = "night"
    game["day"] = 1
    reset_night(chat_id)
    reset_votes(chat_id)
    return game


# ──────────────────────────────────────────────
#  Night / Vote Reset
# ──────────────────────────────────────────────

def reset_night(chat_id: int):
    game = get_game(chat_id)
    if not game:
        return

    game["night_actions"] = {
        "mafia_votes": {},
        "doctor_save": None,
        "detective_checks": {},
        "bodyguard_user": None,
        "bodyguard_target": None,
        "vigilante_shot": None,
        "cupid_done": game.get("night_actions", {}).get("cupid_done", False),
        "witch_save": None,
        "witch_kill": None,
        "silenced": None,
        "arsonist_ignite": False,
        "trickster_ready": None,
    }


def reset_votes(chat_id: int):
    game = get_game(chat_id)
    if game:
        game["votes"] = {}


# ──────────────────────────────────────────────
#  Night Actions
# ──────────────────────────────────────────────

def mafia_vote(chat_id: int, mafia_id: int, target_id: int):
    game = get_game(chat_id)
    if not game:
        return False, "No active Mafia game."
    if game["status"] != "night":
        return False, "Night action is not active."

    mafia = get_player(game, mafia_id)
    if not mafia or mafia["role"] not in ("mafia", "godfather"):
        return False, "Only Mafia can choose a victim."
    if mafia_id not in game["alive"]:
        return False, "Dead players cannot act."
    if target_id not in game["alive"]:
        return False, "Target is not alive."
    if target_id == mafia_id:
        return False, "You cannot target yourself."

    target = get_player(game, target_id)
    if target and target["role"] in ("mafia", "godfather"):
        return False, "You cannot kill another Mafia member."

    game["night_actions"]["mafia_votes"][mafia_id] = target_id
    return True, "Victim selected."


def doctor_save(chat_id: int, doctor_id: int, target_id: int):
    game = get_game(chat_id)
    if not game:
        return False, "No active Mafia game."
    if game["status"] != "night":
        return False, "Doctor acts only at night."

    doctor = get_player(game, doctor_id)
    if not doctor or doctor["role"] != "doctor":
        return False, "Only Doctor can protect."
    if doctor_id not in game["alive"]:
        return False, "Dead players cannot act."
    if target_id not in game["alive"]:
        return False, "Target is not alive."

    # Cannot save the same player two nights in a row
    if game.get("last_doctor_save") == target_id:
        return False, "Doctor cannot protect the same player two nights in a row."

    # Self-save limit
    if target_id == doctor_id:
        used = doctor.get("doctor_self_saves", 0)
        if used >= DOCTOR_SELF_SAVE_LIMIT:
            return False, f"You can only save yourself {DOCTOR_SELF_SAVE_LIMIT} times per game."
        doctor["doctor_self_saves"] = used + 1

    game["night_actions"]["doctor_save"] = target_id
    reset_afk(game, doctor_id)
    return True, "Protection selected."


def detective_check(chat_id: int, detective_id: int, target_id: int):
    game = get_game(chat_id)
    if not game:
        return False, "No active Mafia game.", None
    if game["status"] != "night":
        return False, "Detective acts only at night.", None

    detective = get_player(game, detective_id)
    if not detective or detective["role"] != "detective":
        return False, "Only Detective can investigate.", None
    if detective_id not in game["alive"]:
        return False, "Dead players cannot act.", None
    if target_id not in game["alive"]:
        return False, "Target is not alive.", None
    if target_id == detective_id:
        return False, "You cannot investigate yourself.", None

    target = get_player(game, target_id)
    game["night_actions"]["detective_checks"][detective_id] = target_id
    reset_afk(game, detective_id)

    # Godfather appears innocent to detective
    is_mafia = target["role"] == "mafia"   # godfather returns False (innocent)
    return True, "Investigation complete.", is_mafia


def bodyguard_protect(chat_id: int, guard_id: int, target_id: int):
    game = get_game(chat_id)
    if not game:
        return False, "No active Mafia game."
    if game["status"] != "night":
        return False, "Bodyguard acts only at night."

    guard = get_player(game, guard_id)
    if not guard or guard["role"] != "bodyguard":
        return False, "Only Bodyguard can protect."
    if guard_id not in game["alive"]:
        return False, "Dead players cannot act."
    if target_id not in game["alive"]:
        return False, "Target is not alive."
    if target_id == guard_id:
        return False, "Bodyguard cannot protect themselves."

    game["night_actions"]["bodyguard_user"] = guard_id
    game["night_actions"]["bodyguard_target"] = target_id
    reset_afk(game, guard_id)
    return True, "Guard target selected."


def vigilante_shoot(chat_id: int, vigilante_id: int, target_id: int):
    game = get_game(chat_id)
    if not game:
        return False, "No active Mafia game."
    if game["status"] != "night":
        return False, "Vigilante acts only at night."

    vig = get_player(game, vigilante_id)
    if not vig or vig["role"] != "vigilante":
        return False, "Only Vigilante can shoot."
    if vigilante_id not in game["alive"]:
        return False, "Dead players cannot act."
    if target_id not in game["alive"]:
        return False, "Target is not alive."
    if target_id == vigilante_id:
        return False, "You cannot shoot yourself."

    game["night_actions"]["vigilante_shot"] = {
        "shooter": vigilante_id,
        "target": target_id,
    }
    reset_afk(game, vigilante_id)
    return True, "Shot selected."


def witch_save(chat_id: int, witch_id: int, target_id: int):
    game = get_game(chat_id)
    if not game:
        return False, "No active Mafia game."
    if game["status"] != "night":
        return False, "Witch acts only at night."

    witch = get_player(game, witch_id)
    if not witch or witch["role"] != "witch":
        return False, "Only Velvet Witch can use potions."
    if witch.get("witch_save_used"):
        return False, "Your save potion is already used."
    if target_id not in game["alive"]:
        return False, "Target is not alive."

    witch["witch_save_used"] = True
    game["night_actions"]["witch_save"] = target_id
    reset_afk(game, witch_id)
    return True, "Save potion used."


def witch_kill(chat_id: int, witch_id: int, target_id: int):
    game = get_game(chat_id)
    if not game:
        return False, "No active Mafia game."
    if game["status"] != "night":
        return False, "Witch acts only at night."

    witch = get_player(game, witch_id)
    if not witch or witch["role"] != "witch":
        return False, "Only Velvet Witch can use potions."
    if witch.get("witch_kill_used"):
        return False, "Your kill potion is already used."
    if target_id not in game["alive"]:
        return False, "Target is not alive."

    witch["witch_kill_used"] = True
    game["night_actions"]["witch_kill"] = target_id
    reset_afk(game, witch_id)
    return True, "Kill potion used."


def silence_player(chat_id: int, silencer_id: int, target_id: int):
    game = get_game(chat_id)
    if not game:
        return False, "No active Mafia game."
    if game["status"] != "night":
        return False, "Silence Broker acts only at night."

    silencer = get_player(game, silencer_id)
    if not silencer or silencer["role"] != "silencer":
        return False, "Only Silence Broker can silence."
    if target_id not in game["alive"]:
        return False, "Target is not alive."

    game["night_actions"]["silenced"] = target_id
    reset_afk(game, silencer_id)
    return True, "Player silenced."


def arsonist_mark(chat_id: int, arsonist_id: int, target_id: int):
    game = get_game(chat_id)
    if not game:
        return False, "No active Mafia game."

    arsonist = get_player(game, arsonist_id)
    if not arsonist or arsonist["role"] != "arsonist":
        return False, "Only Flame Gambler can mark."
    if target_id not in game["alive"]:
        return False, "Target is not alive."

    marked = game.setdefault("arsonist_marks", [])
    if target_id not in marked:
        marked.append(target_id)

    reset_afk(game, arsonist_id)
    return True, "Target marked with flame."


def arsonist_ignite(chat_id: int, arsonist_id: int):
    game = get_game(chat_id)
    if not game:
        return False, "No active Mafia game."

    arsonist = get_player(game, arsonist_id)
    if not arsonist or arsonist["role"] != "arsonist":
        return False, "Only Flame Gambler can ignite."

    marks = game.get("arsonist_marks", [])
    if not marks:
        return False, "No marked players to ignite."

    game["night_actions"]["arsonist_ignite"] = True
    reset_afk(game, arsonist_id)
    return True, "Flames prepared."


def cupid_link(chat_id: int, cupid_id: int, user1_id: int, user2_id: int):
    game = get_game(chat_id)
    if not game:
        return False, "No active Mafia game."
    if game["status"] != "night" or game["day"] != 1:
        return False, "Cupid can only link lovers on Night 1."

    cupid = get_player(game, cupid_id)
    if not cupid or cupid["role"] != "cupid":
        return False, "Only Cupid can link lovers."
    if cupid_id not in game["alive"]:
        return False, "Dead players cannot act."
    if game["night_actions"].get("cupid_done"):
        return False, "Cupid already linked lovers."
    if user1_id == user2_id:
        return False, "Choose two different players."
    if user1_id not in game["alive"] or user2_id not in game["alive"]:
        return False, "Both lovers must be alive."

    game["lovers"] = [user1_id, user2_id]
    game["night_actions"]["cupid_done"] = True
    return True, "Lovers linked."


def trickster_twist(chat_id: int, trickster_id: int):
    game = get_game(chat_id)
    if not game:
        return False, "No active Mafia game."
    if game["status"] != "voting":
        return False, "Trickster can only twist during voting."

    trickster = get_player(game, trickster_id)
    if not trickster or trickster["role"] != "trickster":
        return False, "Only Fate Trickster can twist votes."
    if trickster_id not in game["alive"]:
        return False, "Dead players cannot act."
    if trickster.get("trickster_used"):
        return False, "You already used your twist."

    trickster["trickster_used"] = True
    game["night_actions"]["trickster_ready"] = trickster_id
    return True, "Vote twist activated."


# ──────────────────────────────────────────────
#  Night Resolution  ← PRIMARY BUG FIX
# ──────────────────────────────────────────────

def _get_mafia_target(game: dict):
    votes = game["night_actions"].get("mafia_votes", {})
    if not votes:
        return None

    counts: dict = {}
    for target_id in votes.values():
        counts[target_id] = counts.get(target_id, 0) + 1

    highest = max(counts.values())
    top = [uid for uid, count in counts.items() if count == highest]
    return random.choice(top)


def resolve_night(chat_id: int) -> dict:
    """
    Resolve all night actions in correct priority order:
    1. Doctor save (cancels mafia kill on that target)
    2. Witch save (cancels mafia kill on that target)
    3. Bodyguard guard (bodyguard dies instead of guarded target)
    4. Mafia kill (if not saved/guarded)
    5. Vigilante shot
    6. Witch kill
    7. Arsonist ignite
    8. Lover chain deaths
    """
    game = get_game(chat_id)
    if not game:
        return {}

    na = game["night_actions"]
    target_id    = _get_mafia_target(game)
    saved_id     = na.get("doctor_save")       # doctor's chosen save target
    witch_save_id = na.get("witch_save")        # witch's save potion target
    guard_target = na.get("bodyguard_target")
    guard_id     = na.get("bodyguard_user")
    vig          = na.get("vigilante_shot")
    witch_kill_id = na.get("witch_kill")
    arson_ignite = na.get("arsonist_ignite", False)
    arson_marks  = game.get("arsonist_marks", [])

    result: dict = {
        "target":          None,
        "killed":          None,
        "saved":           False,   # doctor saved
        "witch_saved":     False,   # witch potion saved
        "guarded":         False,   # bodyguard blocked
        "bodyguard_dead":  None,
        "vigilante_killed": None,
        "witch_killed":    None,
        "arson_killed":    [],
        "lover_dead":      None,
        "note":            random.choice(DEATH_NOTES),
    }

    if target_id:
        result["target"] = get_player(game, target_id)

    # ── Mafia kill resolution (with saves) ──────────────────────────────────
    if target_id:
        if target_id == saved_id:
            # Doctor protected this exact player → nobody dies from mafia tonight
            result["saved"] = True

        elif target_id == witch_save_id:
            # Witch used save potion on this player → nobody dies from mafia tonight
            result["witch_saved"] = True

        elif guard_target == target_id and guard_id and guard_id in game["alive"]:
            # Bodyguard guarded this player → bodyguard dies instead
            result["guarded"] = True
            result["bodyguard_dead"] = kill_player(game, guard_id)
            # The guarded player SURVIVES — do NOT kill target_id

        else:
            # No protection → player dies
            killed = kill_player(game, target_id)
            result["killed"] = killed

            if killed:
                result["lover_dead"] = kill_lover_if_needed(game, killed["id"])

    # ── Vigilante shot ───────────────────────────────────────────────────────
    if vig:
        shot_target = vig.get("target")
        if shot_target and shot_target in game["alive"]:
            killed = kill_player(game, shot_target)
            result["vigilante_killed"] = killed

            if killed and not result["lover_dead"]:
                result["lover_dead"] = kill_lover_if_needed(game, killed["id"])

    # ── Witch kill potion ────────────────────────────────────────────────────
    if witch_kill_id and witch_kill_id in game["alive"]:
        killed = kill_player(game, witch_kill_id)
        result["witch_killed"] = killed

        if killed and not result["lover_dead"]:
            result["lover_dead"] = kill_lover_if_needed(game, killed["id"])

    # ── Arsonist ignite ──────────────────────────────────────────────────────
    if arson_ignite and arson_marks:
        burned = []
        for uid in list(arson_marks):
            if uid in game["alive"]:
                killed = kill_player(game, uid)
                if killed:
                    burned.append(killed)
                    if not result["lover_dead"]:
                        result["lover_dead"] = kill_lover_if_needed(game, killed["id"])

        result["arson_killed"] = burned
        game["arsonist_marks"] = []

    # ── Bookkeeping ──────────────────────────────────────────────────────────
    # Remember who the doctor saved this night so they can't save same player next night
    game["last_doctor_save"] = saved_id
    game["status"] = "discussion"

    return result


# ──────────────────────────────────────────────
#  Voting
# ──────────────────────────────────────────────

def start_voting(chat_id: int):
    game = get_game(chat_id)
    if not game:
        return
    game["status"] = "voting"
    reset_votes(chat_id)


def vote_player(chat_id: int, voter_id: int, target_id):
    game = get_game(chat_id)
    if not game:
        return False, "No active Mafia game."
    if game["status"] != "voting":
        return False, "Voting is not active."
    if voter_id not in game["alive"]:
        return False, "Dead players cannot vote."
    if target_id != "skip" and target_id not in game["alive"]:
        return False, "Target is not alive."
    if voter_id == target_id:
        return False, "You cannot vote for yourself."

    game["votes"][voter_id] = target_id
    reset_afk(game, voter_id)
    return True, "Vote recorded."


def resolve_votes(chat_id: int) -> dict:
    game = get_game(chat_id)
    if not game:
        return {}

    empty_result = {
        "eliminated": None,
        "tie": False,
        "skip": False,
        "jester_win": False,
        "lover_dead": None,
        "counts": {},
    }

    if not game["votes"]:
        game["status"] = "night"
        game["day"] += 1
        reset_night(chat_id)
        return {**empty_result, "skip": True}

    # Tally votes (mayor counts as 2)
    counts: dict = {}
    for voter_id, target_id in game["votes"].items():
        voter = get_player(game, voter_id)
        weight = 2 if voter and voter["role"] == "mayor" else 1
        counts[target_id] = counts.get(target_id, 0) + weight

    # Trickster swaps top two
    if game.get("night_actions", {}).get("trickster_ready") and len(counts) >= 2:
        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        first_id, first_votes = sorted_counts[0]
        second_id, second_votes = sorted_counts[1]
        counts[first_id] = second_votes
        counts[second_id] = first_votes

    # Handle skip votes
    if "skip" in counts:
        del counts["skip"]

    if not counts:
        game["status"] = "night"
        game["day"] += 1
        reset_night(chat_id)
        return {**empty_result, "skip": True}

    highest = max(counts.values())
    top = [uid for uid, count in counts.items() if count == highest]

    if len(top) > 1:
        game["status"] = "night"
        game["day"] += 1
        reset_night(chat_id)
        return {**empty_result, "tie": True, "counts": counts}

    eliminated_id = top[0]
    eliminated = kill_player(game, eliminated_id)
    lover_dead = kill_lover_if_needed(game, eliminated_id)

    game["status"] = "night"
    game["day"] += 1
    reset_night(chat_id)

    return {
        "eliminated": eliminated,
        "tie": False,
        "skip": False,
        "jester_win": bool(eliminated and eliminated["role"] == "jester"),
        "lover_dead": lover_dead,
        "counts": counts,
    }


# ──────────────────────────────────────────────
#  Win Condition
# ──────────────────────────────────────────────

def check_winner(chat_id: int):
    game = get_game(chat_id)
    if not game:
        return None

    mafia = alive_mafia(game)
    town = alive_town(game)

    if len(mafia) == 0:
        return "town"
    if len(mafia) >= len(town):
        return "mafia"
    return None


# ──────────────────────────────────────────────
#  Last Words
# ──────────────────────────────────────────────

def can_send_last_words(user_id: int):
    """Return the game dict if user is in a valid last-words window, else None."""
    for game in active_mafia_games.values():
        entry = game.get("last_words_waiting", {}).get(user_id)
        if not entry:
            continue

        if entry.get("used"):
            return None

        if datetime.utcnow() > entry["expires_at"]:
            # Window expired — clean up
            game["last_words_waiting"].pop(user_id, None)
            return None

        return game

    return None


def mark_last_words_used(game: dict, user_id: int):
    entry = game.get("last_words_waiting", {}).get(user_id)
    if entry:
        entry["used"] = True

    player = game["players"].get(user_id)
    if player:
        player["last_words_used"] = True

    game.get("last_words_waiting", {}).pop(user_id, None)


# ──────────────────────────────────────────────
#  MVP & Rewards  ← BUG FIX: reward_game logic fixed
# ──────────────────────────────────────────────

def calculate_mvp(game: dict, winner: str):
    candidates = []

    for user_id, player in game["players"].items():
        score = 0
        role = player.get("role")

        if winner == "mafia" and role in ("mafia", "godfather"):
            score += 50
        elif winner == "town" and role not in ("mafia", "godfather", "jester"):
            score += 50
        elif winner == "jester" and role == "jester":
            score += 80

        if player.get("alive"):
            score += 15
        if role == "doctor" and game.get("last_doctor_save"):
            score += 10
        if role == "bodyguard" and not player.get("alive"):
            score += 20
        if role == "mayor":
            score += 10
        if role == "witch":
            if player.get("witch_save_used"):
                score += 10
            if player.get("witch_kill_used"):
                score += 10
        if role == "arsonist":
            score += len(game.get("arsonist_marks", [])) * 3

        candidates.append((score, player))

    if not candidates:
        return None

    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]


async def reward_game(chat_id: int, winner: str):
    """
    BUG FIX: previously the else (add_loss) ran even for winners
    because the structure was if/elif/else without proper mutual exclusion.
    Now properly separated.
    """
    game = get_game(chat_id)
    if not game:
        return

    mvp = calculate_mvp(game, winner)

    for user_id, player in game["players"].items():
        role = player.get("role")

        # ── Jester winner ───────────────────────────────────────────────────
        if winner == "jester" and role == "jester":
            await add_jester_win(user_id)
            await add_win(user_id, coins=JESTER_COINS, xp=JESTER_XP)
            if mvp and user_id == mvp.get("id"):
                await add_win(user_id, coins=50, xp=50)
            continue

        # ── Regular winner check ────────────────────────────────────────────
        is_winner = False

        if winner == "mafia" and role in ("mafia", "godfather"):
            is_winner = True
        elif winner == "town" and role not in ("mafia", "godfather", "jester"):
            is_winner = True

        if is_winner:
            await add_mafia_win(user_id)
            await add_win(user_id, coins=WIN_COINS, xp=WIN_XP)
            if mvp and user_id == mvp.get("id"):
                await add_win(user_id, coins=50, xp=50)
        else:
            # Loser — only losers reach here
            await add_mafia_loss(user_id)
            await add_loss(user_id, xp=LOSE_XP)

    await add_group_game(chat_id)


# ──────────────────────────────────────────────
#  UI Helpers
# ──────────────────────────────────────────────

def join_button():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("🪑 Take A Seat", callback_data="mafia_join")]]
    )


def format_alive(game: dict) -> str:
    if not game or not game["alive"]:
        return "No alive players."

    lines = []
    for i, uid in enumerate(game["alive"], start=1):
        player = game["players"].get(uid)
        if player:
            lines.append(f'{i}. <a href="tg://user?id={uid}">{player["name"]}</a>')

    return "\n".join(lines)


def format_players(game: dict) -> str:
    if not game or not game["players"]:
        return "No players joined."

    lines = []
    for i, player in enumerate(game["players"].values(), start=1):
        uid = player["id"]
        lines.append(f'{i}. <a href="tg://user?id={uid}">{player["name"]}</a>')

    return "\n".join(lines)


def format_roles(game: dict) -> str:
    lines = []
    for player in game["players"].values():
        status = "Alive" if player["alive"] else "Dead"
        uid = player["id"]
        lines.append(
            f'{role_name(player["role"])} — '
            f'<a href="tg://user?id={uid}">{player["name"]}</a> · '
            f'<i>{status}</i>'
        )
    return "\n".join(lines)