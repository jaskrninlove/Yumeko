from yumeko.games.mafia.game import active_mafia_games


def get_silenced_player(chat_id: int):
    game = active_mafia_games.get(chat_id)

    if not game:
        return None

    return game.get("night_actions", {}).get("silenced")