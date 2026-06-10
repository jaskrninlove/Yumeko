# ==========================================================
#  Yumeko Games Bot — Mystery Box Royale Engine
#  Copyright (c) 2026 Jass
# ==========================================================

import random
from datetime import datetime

active_games = {}

MIN_PLAYERS = 2
MAX_PLAYERS = 15
BOARD_SIZE = 4
TOTAL_BOXES = BOARD_SIZE * BOARD_SIZE

WIN_COINS = 150
WIN_XP = 60
LOSE_XP = 10

BOX_EMOJI = "🎁"
OPENED_EMOJI = "⬜"
DEAD_EMOJI = "💀"

REWARD_POOL = [
    {"type": "coins", "amount": 20, "weight": 20, "emoji": "💰", "name": "+20 Coins"},
    {"type": "coins", "amount": 35, "weight": 18, "emoji": "💰", "name": "+35 Coins"},
    {"type": "coins", "amount": 60, "weight": 12, "emoji": "💎", "name": "+60 Coins"},
    {"type": "xp", "amount": 15, "weight": 16, "emoji": "⭐", "name": "+15 XP"},
    {"type": "xp", "amount": 30, "weight": 10, "emoji": "🌟", "name": "+30 XP"},
    {"type": "shield", "amount": 1, "weight": 9, "emoji": "🛡", "name": "Shield"},
    {"type": "bonus_turn", "amount": 1, "weight": 7, "emoji": "🎟", "name": "Bonus Turn"},
    {"type": "steal", "amount": 1, "weight": 5, "emoji": "⚔️", "name": "Coin Steal"},
    {"type": "curse", "amount": 1, "weight": 5, "emoji": "👻", "name": "Curse"},
    {"type": "bomb", "amount": 1, "weight": 4, "emoji": "🧨", "name": "Bomb"},
    {"type": "death", "amount": 1, "weight": 3, "emoji": "💀", "name": "Death Box"},
    {"type": "crown", "amount": 1, "weight": 3, "emoji": "👑", "name": "Crown"},
    {"type": "jackpot", "amount": 1, "weight": 1, "emoji": "🎰", "name": "JACKPOT"},
]


def now_utc():
    return datetime.utcnow()


def create_game(chat_id: int, host):
    game = {
        "chat_id": chat_id,
        "host_id": host.id,
        "host_name": host.first_name or "Player",
        "status": "joining",
        "players": {},
        "order": [],
        "alive": set(),
        "turn_index": 0,
        "board": [],
        "opened": set(),
        "pending_steal": None,
        "round": 1,
        "created_at": now_utc(),
    }

    active_games[chat_id] = game
    join_game(chat_id, host)
    return game


def get_game(chat_id: int):
    return active_games.get(chat_id)


def end_game(chat_id: int):
    active_games.pop(chat_id, None)


def join_game(chat_id: int, user):
    game = get_game(chat_id)

    if not game:
        return False, "no_game"

    if game["status"] != "joining":
        return False, "started"

    if user.id in game["players"]:
        return False, "joined"

    if len(game["players"]) >= MAX_PLAYERS:
        return False, "full"

    game["players"][user.id] = {
        "id": user.id,
        "name": user.first_name or "Player",
        "alive": True,
        "coins": 0,
        "xp": 0,
        "crowns": 0,
        "jackpots": 0,
        "shields": 0,
        "boxes_opened": 0,
        "bonus_turns": 0,
        "curses": 0,
        "bombs_survived": 0,
        "kills": 0,
    }

    game["order"].append(user.id)
    game["alive"].add(user.id)
    return True, "joined"


def format_players(game):
    lines = []

    for index, uid in enumerate(game["order"], 1):
        player = game["players"][uid]
        status = "🟢" if player["alive"] else "💀"
        shields = f" 🛡{player['shields']}" if player["shields"] else ""
        crowns = f" 👑{player['crowns']}" if player["crowns"] else ""

        lines.append(
            f"{index}. {status} "
            f"<a href='tg://user?id={uid}'><b>{player['name']}</b></a>"
            f"{shields}{crowns}"
        )

    return "\n".join(lines)


def weighted_reward():
    total_weight = sum(item["weight"] for item in REWARD_POOL)
    pick = random.uniform(0, total_weight)

    current = 0

    for item in REWARD_POOL:
        current += item["weight"]
        if pick <= current:
            return dict(item)

    return dict(REWARD_POOL[0])


def build_board():
    board = []

    for idx in range(TOTAL_BOXES):
        reward = weighted_reward()
        board.append(
            {
                "id": idx,
                "opened": False,
                "emoji": BOX_EMOJI,
                "revealed": reward["emoji"],
                "reward": reward,
            }
        )

    return board


def start_game(chat_id: int):
    game = get_game(chat_id)

    if not game:
        return False, "no_game"

    if len(game["players"]) < MIN_PLAYERS:
        return False, "not_enough"

    game["status"] = "playing"
    game["board"] = build_board()
    game["opened"] = set()
    game["turn_index"] = 0
    game["round"] = 1
    game["pending_steal"] = None

    for uid in game["players"]:
        game["players"][uid]["alive"] = True
        game["players"][uid]["coins"] = 0
        game["players"][uid]["xp"] = 0
        game["players"][uid]["crowns"] = 0
        game["players"][uid]["jackpots"] = 0
        game["players"][uid]["shields"] = 0
        game["players"][uid]["boxes_opened"] = 0
        game["players"][uid]["bonus_turns"] = 0
        game["players"][uid]["curses"] = 0
        game["players"][uid]["bombs_survived"] = 0
        game["players"][uid]["kills"] = 0

    game["alive"] = set(game["order"])
    normalize_turn(game)

    return True, "started"


def alive_players(game):
    return [uid for uid in game["order"] if uid in game["alive"]]


def current_player_id(game):
    alive = alive_players(game)

    if not alive:
        return None

    if game["turn_index"] >= len(alive):
        game["turn_index"] = 0

    return alive[game["turn_index"]]


def current_player(game):
    uid = current_player_id(game)

    if uid is None:
        return None

    return game["players"].get(uid)


def normalize_turn(game):
    alive = alive_players(game)

    if not alive:
        game["turn_index"] = 0
        return

    if game["turn_index"] >= len(alive):
        game["turn_index"] = 0


def next_turn(game):
    alive = alive_players(game)

    if len(alive) <= 1:
        return

    game["turn_index"] += 1

    if game["turn_index"] >= len(alive):
        game["turn_index"] = 0

    game["round"] += 1


def eliminate_player(game, user_id: int):
    if user_id in game["alive"]:
        game["alive"].discard(user_id)

    if user_id in game["players"]:
        game["players"][user_id]["alive"] = False

    normalize_turn(game)


def board_text(game, reveal: bool = False):
    rows = []

    for r in range(BOARD_SIZE):
        line = ""

        for c in range(BOARD_SIZE):
            idx = r * BOARD_SIZE + c
            cell = game["board"][idx]

            if cell["opened"] or reveal:
                line += cell["revealed"]
            else:
                line += BOX_EMOJI

        rows.append(line)

    return "\n".join(rows)


def unopened_boxes(game):
    return [cell for cell in game["board"] if not cell["opened"]]


def is_game_over(game):
    return len(alive_players(game)) <= 1 or len(unopened_boxes(game)) == 0


def get_winner(game):
    alive = alive_players(game)

    if len(alive) == 1:
        return alive[0]

    if not alive:
        return None

    # If board ends without deaths, winner is richest by in-game coins + crowns.
    return max(
        alive,
        key=lambda uid: (
            game["players"][uid]["crowns"],
            game["players"][uid]["jackpots"],
            game["players"][uid]["coins"],
            game["players"][uid]["xp"],
        ),
    )


def open_box(chat_id: int, user_id: int, box_id: int):
    game = get_game(chat_id)

    if not game:
        return False, "no_game", None

    if game["status"] != "playing":
        return False, "not_playing", None

    if game.get("pending_steal"):
        return False, "pending_steal", None

    if user_id not in game["players"]:
        return False, "not_player", None

    if user_id not in game["alive"]:
        return False, "dead", None

    if current_player_id(game) != user_id:
        return False, "not_turn", None

    if box_id < 0 or box_id >= len(game["board"]):
        return False, "invalid", None

    cell = game["board"][box_id]

    if cell["opened"]:
        return False, "opened", None

    player = game["players"][user_id]
    reward = cell["reward"]

    cell["opened"] = True
    player["boxes_opened"] += 1

    result = {
        "box_id": box_id,
        "reward": reward,
        "player": player,
        "eliminated": False,
        "shield_used": False,
        "bonus_turn": False,
        "needs_steal_target": False,
        "winner": None,
        "game_over": False,
        "message_key": reward["type"],
    }

    reward_type = reward["type"]
    amount = reward["amount"]

    if reward_type == "coins":
        player["coins"] += amount

    elif reward_type == "xp":
        player["xp"] += amount

    elif reward_type == "shield":
        player["shields"] += 1

    elif reward_type == "bonus_turn":
        player["bonus_turns"] += 1
        result["bonus_turn"] = True

    elif reward_type == "steal":
        targets = steal_targets(game, user_id)

        if targets:
            game["pending_steal"] = {
                "from": user_id,
                "amount": random.randint(25, 75),
            }
            result["needs_steal_target"] = True
        else:
            player["coins"] += 25
            result["message_key"] = "steal_empty"

    elif reward_type == "curse":
        player["curses"] += 1
        if player["coins"] >= 30:
            player["coins"] -= 30
        else:
            player["xp"] = max(0, player["xp"] - 10)

    elif reward_type == "bomb":
        if player["shields"] > 0:
            player["shields"] -= 1
            player["bombs_survived"] += 1
            result["shield_used"] = True
        else:
            result["eliminated"] = True
            eliminate_player(game, user_id)

    elif reward_type == "death":
        if player["shields"] > 0:
            player["shields"] -= 1
            result["shield_used"] = True
        else:
            result["eliminated"] = True
            eliminate_player(game, user_id)

    elif reward_type == "crown":
        player["crowns"] += 1
        player["coins"] += 75
        player["xp"] += 25

    elif reward_type == "jackpot":
        player["jackpots"] += 1
        player["coins"] += 500
        player["xp"] += 100
        player["crowns"] += 1

    if is_game_over(game):
        result["game_over"] = True
        result["winner"] = get_winner(game)
        game["status"] = "finished"
        return True, "opened", result

    if not result["bonus_turn"] and not result["needs_steal_target"]:
        next_turn(game)

    return True, "opened", result


def steal_targets(game, user_id: int):
    targets = []

    for uid in alive_players(game):
        if uid == user_id:
            continue

        player = game["players"][uid]

        if player["coins"] > 0:
            targets.append(uid)

    return targets


def apply_steal(chat_id: int, thief_id: int, target_id: int):
    game = get_game(chat_id)

    if not game:
        return False, "no_game", None

    pending = game.get("pending_steal")

    if not pending:
        return False, "no_steal", None

    if pending["from"] != thief_id:
        return False, "not_thief", None

    if target_id not in game["players"]:
        return False, "invalid_target", None

    if target_id not in game["alive"]:
        return False, "dead_target", None

    if target_id == thief_id:
        return False, "self", None

    thief = game["players"][thief_id]
    target = game["players"][target_id]

    amount = min(target["coins"], pending["amount"])

    target["coins"] -= amount
    thief["coins"] += amount
    thief["kills"] += 1

    game["pending_steal"] = None

    if is_game_over(game):
        winner = get_winner(game)
        game["status"] = "finished"
    else:
        winner = None
        next_turn(game)

    return True, "stolen", {
        "thief": thief,
        "target": target,
        "amount": amount,
        "winner": winner,
        "game_over": winner is not None,
    }


def player_summary(player):
    return (
        f"💰 Coins: <b>{player['coins']}</b>\n"
        f"⭐ XP: <b>{player['xp']}</b>\n"
        f"👑 Crowns: <b>{player['crowns']}</b>\n"
        f"🎰 Jackpots: <b>{player['jackpots']}</b>\n"
        f"🛡 Shields: <b>{player['shields']}</b>\n"
        f"🎁 Boxes: <b>{player['boxes_opened']}</b>"
    )


def final_scoreboard(game):
    ordered = sorted(
        game["players"].values(),
        key=lambda p: (
            p["alive"],
            p["crowns"],
            p["jackpots"],
            p["coins"],
            p["xp"],
            p["boxes_opened"],
        ),
        reverse=True,
    )

    lines = []

    for index, player in enumerate(ordered, 1):
        status = "🏆" if index == 1 else ("🟢" if player["alive"] else "💀")
        lines.append(
            f"{index}. {status} <b>{player['name']}</b> — "
            f"💰{player['coins']} ⭐{player['xp']} 👑{player['crowns']} 🎰{player['jackpots']}"
        )

    return "\n".join(lines)