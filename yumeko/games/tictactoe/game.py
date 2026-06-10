# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
# ==========================================================

import random
from datetime import datetime

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from yumeko.database.users import add_win, add_loss, add_xp
from yumeko.database.groups import add_group_game


active_tictactoe_games = {}

JOIN_TIME = 45
TURN_TIME = 45

WIN_COINS = 60
WIN_XP = 35
LOSE_XP = 10
DRAW_XP = 15

EMPTY = "⬜"
X_MARK = "❌"
O_MARK = "⭕"


def create_game(chat_id: int, host):
    active_tictactoe_games[chat_id] = {
        "chat_id": chat_id,
        "host_id": host.id,
        "host_name": host.first_name or "Unknown",
        "players": {},
        "symbols": {},
        "board": [None] * 9,
        "turn": None,
        "turn_token": 0,
        "status": "joining",
        "message_id": None,
        "created_at": datetime.utcnow(),
    }


def get_game(chat_id: int):
    return active_tictactoe_games.get(chat_id)


def end_game(chat_id: int):
    active_tictactoe_games.pop(chat_id, None)


def set_message(chat_id: int, message_id: int):
    game = get_game(chat_id)
    if game:
        game["message_id"] = message_id


def join_game(chat_id: int, user):
    game = get_game(chat_id)

    if not game:
        return False, "no_game"

    if game["status"] != "joining":
        return False, "started"

    if user.id in game["players"]:
        return False, "already_joined"

    if len(game["players"]) >= 2:
        return False, "full"

    game["players"][user.id] = {
        "id": user.id,
        "name": user.first_name or "Unknown",
        "username": user.username,
    }

    return True, "joined"


def start_game(chat_id: int):
    game = get_game(chat_id)

    if not game or len(game["players"]) < 2:
        return False

    players = list(game["players"].keys())
    random.shuffle(players)

    game["symbols"][players[0]] = X_MARK
    game["symbols"][players[1]] = O_MARK
    game["turn"] = players[0]
    game["status"] = "running"
    game["turn_token"] += 1

    return True


def get_player(game: dict, user_id: int):
    return game["players"].get(user_id)


def get_current_player(game: dict):
    if not game or not game.get("turn"):
        return None

    return game["players"].get(game["turn"])


def switch_turn(game: dict):
    player_ids = list(game["players"].keys())

    for uid in player_ids:
        if uid != game["turn"]:
            game["turn"] = uid
            break

    game["turn_token"] += 1


def make_move(chat_id: int, user_id: int, index: int):
    game = get_game(chat_id)

    if not game:
        return False, "no_game"

    if game["status"] != "running":
        return False, "not_running"

    if user_id not in game["players"]:
        return False, "not_player"

    if game["turn"] != user_id:
        return False, "not_turn"

    if index < 0 or index > 8:
        return False, "invalid"

    if game["board"][index] is not None:
        return False, "taken"

    game["board"][index] = user_id

    winner = check_winner(game)

    if winner:
        game["status"] = "finished"
        return True, {"type": "win", "winner": winner}

    if is_draw(game):
        game["status"] = "finished"
        return True, {"type": "draw"}

    switch_turn(game)
    return True, {"type": "continue"}


def check_winner(game: dict):
    wins = [
        (0, 1, 2),
        (3, 4, 5),
        (6, 7, 8),
        (0, 3, 6),
        (1, 4, 7),
        (2, 5, 8),
        (0, 4, 8),
        (2, 4, 6),
    ]

    board = game["board"]

    for a, b, c in wins:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]

    return None


def is_draw(game: dict):
    return all(cell is not None for cell in game["board"])


def board_buttons(game: dict):
    rows = []

    for r in range(3):
        row = []

        for c in range(3):
            index = r * 3 + c
            owner = game["board"][index]

            if owner:
                text = game["symbols"].get(owner, "❔")
            else:
                text = EMPTY

            row.append(
                InlineKeyboardButton(
                    text,
                    callback_data=f"ttt_move_{index}",
                )
            )

        rows.append(row)

    rows.append(
        [
            InlineKeyboardButton(
                "🛑 Stop Game",
                callback_data="ttt_stop",
            )
        ]
    )

    return InlineKeyboardMarkup(rows)


def join_button():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🎭 Accept Duel",
                    callback_data="ttt_join",
                )
            ]
        ]
    )


async def reward_win(chat_id: int, winner_id: int):
    game = get_game(chat_id)

    if not game:
        return

    for uid in game["players"]:
        if uid == winner_id:
            await add_win(uid, coins=WIN_COINS, xp=WIN_XP)
        else:
            await add_loss(uid, xp=LOSE_XP)

    await add_group_game(chat_id)


async def reward_draw(chat_id: int):
    game = get_game(chat_id)

    if not game:
        return

    for uid in game["players"]:
        await add_xp(uid, DRAW_XP)

    await add_group_game(chat_id)


def format_players(game: dict):
    if not game or not game["players"]:
        return "No players seated."

    lines = []

    for uid, player in game["players"].items():
        symbol = game["symbols"].get(uid, "🎴")
        lines.append(
            f'{symbol} <a href="tg://user?id={uid}">{player["name"]}</a>'
        )

    return "\n".join(lines)