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

active_group_games = {}


def is_game_running(chat_id: int) -> bool:
    return chat_id in active_group_games


def get_running_game(chat_id: int):
    return active_group_games.get(chat_id)


def lock_game(chat_id: int, game_name: str):
    active_group_games[chat_id] = game_name


def unlock_game(chat_id: int):
    active_group_games.pop(chat_id, None)


def force_unlock_game(chat_id: int):
    game = active_group_games.get(chat_id)
    active_group_games.pop(chat_id, None)
    return game