# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
#
#  Developer  : Jass
#  Project    : Yumeko Games Bot
#  Version    : 1.0.0
# ==========================================================

import random
from datetime import datetime
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from yumeko.database.users import add_win, add_loss, add_xp
from yumeko.database.groups import add_group_game


active_blackjack_games = {}

MIN_PLAYERS = 2
MAX_PLAYERS = 10
JOIN_TIME = 30

WIN_COINS = 100
WIN_XP = 50
BLACKJACK_COINS = 150
BLACKJACK_XP = 75
PUSH_XP = 15
LOSE_XP = 8
SURRENDER_XP = 4

SUITS = ["♠️", "♥️", "♦️", "♣️"]
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]


def create_deck():
    deck = []
    for suit in SUITS:
        for rank in RANKS:
            deck.append({"rank": rank, "suit": suit})
    random.shuffle(deck)
    return deck


def card_text(card):
    return f"{card['rank']}{card['suit']}"


def hand_text(cards):
    return " ".join(card_text(card) for card in cards)


def hand_value(cards):
    total = 0
    aces = 0

    for card in cards:
        rank = card["rank"]

        if rank in ["J", "Q", "K"]:
            total += 10
        elif rank == "A":
            total += 11
            aces += 1
        else:
            total += int(rank)

    while total > 21 and aces:
        total -= 10
        aces -= 1

    return total


def is_blackjack(cards):
    return len(cards) == 2 and hand_value(cards) == 21


def create_game(chat_id: int, host_id: int, host_name: str):
    active_blackjack_games[chat_id] = {
        "host_id": host_id,
        "host_name": host_name,
        "players": {},
        "order": [],
        "current_index": 0,
        "dealer": [],
        "deck": create_deck(),
        "status": "joining",
        "started_at": datetime.utcnow(),
    }


def get_game(chat_id: int):
    return active_blackjack_games.get(chat_id)


def end_game(chat_id: int):
    active_blackjack_games.pop(chat_id, None)


def join_game(chat_id: int, user):
    game = get_game(chat_id)

    if not game:
        return False, "no_game"

    if game["status"] != "joining":
        return False, "already_started"

    if user.id in game["players"]:
        return False, "already_joined"

    if len(game["players"]) >= MAX_PLAYERS:
        return False, "full"

    game["players"][user.id] = {
        "id": user.id,
        "name": user.first_name or "Unknown",
        "username": user.username,
        "hand": [],
        "status": "playing",
        "result": None,
        "score": 0,
    }

    game["order"].append(user.id)
    return True, "joined"


def draw_card(game):
    if len(game["deck"]) < 10:
        game["deck"] = create_deck()
    return game["deck"].pop()


def start_game(chat_id: int):
    game = get_game(chat_id)

    if not game:
        return None

    game["status"] = "running"
    game["dealer"] = []

    for _ in range(2):
        for user_id in game["order"]:
            game["players"][user_id]["hand"].append(draw_card(game))
        game["dealer"].append(draw_card(game))

    for user_id in game["order"]:
        player = game["players"][user_id]
        player["score"] = hand_value(player["hand"])

        if is_blackjack(player["hand"]):
            player["status"] = "stand"
            player["result"] = "blackjack"

    game["current_index"] = 0
    advance_to_next_active(chat_id)
    return get_current_player(chat_id)


def get_current_player(chat_id: int):
    game = get_game(chat_id)

    if not game or not game["order"]:
        return None

    if game["current_index"] >= len(game["order"]):
        return None

    user_id = game["order"][game["current_index"]]
    return game["players"].get(user_id)


def advance_to_next_active(chat_id: int):
    game = get_game(chat_id)

    if not game:
        return None

    while game["current_index"] < len(game["order"]):
        player = get_current_player(chat_id)

        if player and player["status"] == "playing":
            return player

        game["current_index"] += 1

    return None


def hit(chat_id: int, user_id: int):
    game = get_game(chat_id)

    if not game:
        return False, "no_game"

    player = get_current_player(chat_id)

    if not player or player["id"] != user_id:
        return False, "not_turn"

    player["hand"].append(draw_card(game))
    player["score"] = hand_value(player["hand"])

    if player["score"] > 21:
        player["status"] = "bust"
        player["result"] = "bust"
        game["current_index"] += 1
        advance_to_next_active(chat_id)
        return True, "bust"

    if player["score"] == 21:
        player["status"] = "stand"
        game["current_index"] += 1
        advance_to_next_active(chat_id)
        return True, "twenty_one"

    return True, "hit"


def stand(chat_id: int, user_id: int):
    game = get_game(chat_id)

    if not game:
        return False, "no_game"

    player = get_current_player(chat_id)

    if not player or player["id"] != user_id:
        return False, "not_turn"

    player["status"] = "stand"
    game["current_index"] += 1
    advance_to_next_active(chat_id)
    return True, "stand"


def surrender(chat_id: int, user_id: int):
    game = get_game(chat_id)

    if not game:
        return False, "no_game"

    player = get_current_player(chat_id)

    if not player or player["id"] != user_id:
        return False, "not_turn"

    player["status"] = "surrender"
    player["result"] = "surrender"
    game["current_index"] += 1
    advance_to_next_active(chat_id)
    return True, "surrender"


def all_players_done(chat_id: int):
    game = get_game(chat_id)

    if not game:
        return False

    return game["current_index"] >= len(game["order"])


def dealer_play(chat_id: int):
    game = get_game(chat_id)

    if not game:
        return None

    while hand_value(game["dealer"]) < 17:
        game["dealer"].append(draw_card(game))

    dealer_score = hand_value(game["dealer"])

    for user_id in game["order"]:
        player = game["players"][user_id]
        score = hand_value(player["hand"])
        player["score"] = score

        if player["result"] in ["bust", "surrender"]:
            continue

        if player["result"] == "blackjack":
            if is_blackjack(game["dealer"]):
                player["result"] = "push"
            else:
                player["result"] = "blackjack_win"
            continue

        if dealer_score > 21:
            player["result"] = "win"
        elif score > dealer_score:
            player["result"] = "win"
        elif score == dealer_score:
            player["result"] = "push"
        else:
            player["result"] = "lose"

    game["status"] = "finished"
    return dealer_score


async def reward_results(chat_id: int):
    game = get_game(chat_id)

    if not game:
        return

    for user_id in game["order"]:
        player = game["players"][user_id]
        result = player["result"]

        if result == "blackjack_win":
            await add_win(user_id, coins=BLACKJACK_COINS, xp=BLACKJACK_XP)
        elif result == "win":
            await add_win(user_id, coins=WIN_COINS, xp=WIN_XP)
        elif result == "push":
            await add_xp(user_id, PUSH_XP)
        elif result == "surrender":
            await add_xp(user_id, SURRENDER_XP)
        else:
            await add_loss(user_id, xp=LOSE_XP)

    await add_group_game(chat_id)


def join_button():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("🎴 Join Blackjack", callback_data="bj_join")]]
    )


def action_buttons():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🃏 Hit", callback_data="bj_hit"),
                InlineKeyboardButton("✋ Stand", callback_data="bj_stand"),
            ],
            [
                InlineKeyboardButton("🏳️ Surrender", callback_data="bj_surrender"),
            ],
        ]
    )


def format_players(game: dict):
    if not game or not game["players"]:
        return "No players joined yet."

    return "\n".join(
        f"{i}. <b>{p['name']}</b>"
        for i, p in enumerate(game["players"].values(), start=1)
    )


def format_hand(player: dict):
    return f"{hand_text(player['hand'])}  ·  <b>{hand_value(player['hand'])}</b>"


def format_final_rows(game: dict):
    rows = []

    labels = {
        "blackjack_win": "🖤 Blackjack Win",
        "win": "🏆 Win",
        "push": "🤝 Push",
        "lose": "💀 Lose",
        "bust": "💥 Bust",
        "surrender": "🏳️ Surrender",
    }

    for user_id in game["order"]:
        p = game["players"][user_id]
        rows.append(
            f"◈ <b>{p['name']}</b> — {hand_text(p['hand'])} "
            f"(<code>{p['score']}</code>) — <b>{labels.get(p['result'], p['result'])}</b>"
        )

    return "\n".join(rows)