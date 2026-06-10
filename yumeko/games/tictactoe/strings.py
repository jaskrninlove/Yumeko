# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
# ==========================================================

from yumeko.games.tictactoe.game import (
    JOIN_TIME,
    TURN_TIME,
    WIN_COINS,
    WIN_XP,
    LOSE_XP,
    DRAW_XP,
    format_players,
)


def lobby_text(game: dict):
    return (
        "<blockquote>♟ <b>Yumeko's Tic Tac Toe Duel</b></blockquote>\n\n"
        "<i>❝ Ahahaha~ A simple game? Darling, every game becomes dangerous when pride is involved. ♡ ❞</i>\n\n"
        f"🎴 Host: <b>{game['host_name']}</b>\n"
        f"👥 Players: <b>{len(game['players'])}/2</b>\n"
        f"⏳ Duel starts in: <b>{JOIN_TIME}s</b>\n\n"
        "<blockquote>🪑 Seated Players</blockquote>\n"
        f"{format_players(game)}\n\n"
        "Tap the button below and challenge fate."
    )


def join_countdown_text(seconds: int):
    return (
        "<blockquote>⏳ <b>Duel Starting Soon</b></blockquote>\n\n"
        f"<i>Only <b>{seconds}s</b> remain before the board opens. ♡</i>"
    )


def not_enough_players():
    return (
        "<blockquote>😔 <b>Duel Cancelled</b></blockquote>\n\n"
        "A proper duel requires two players."
    )


def game_start_text(game: dict):
    players = list(game["players"].keys())

    p1 = game["players"][players[0]]
    p2 = game["players"][players[1]]

    s1 = game["symbols"][players[0]]
    s2 = game["symbols"][players[1]]

    current = game["players"][game["turn"]]

    return (
        "<blockquote>🎭 <b>The Duel Begins</b></blockquote>\n\n"
        "<i>❝ Every move reveals a little about your soul. ♡ ❞</i>\n\n"
        f"{s1} <a href='tg://user?id={players[0]}'>{p1['name']}</a>\n"
        f"{s2} <a href='tg://user?id={players[1]}'>{p2['name']}</a>\n\n"
        f"🎯 Current Turn:\n"
        f"<b><a href='tg://user?id={game['turn']}'>{current['name']}</a></b>\n\n"
        f"⏳ Turn Time: <b>{TURN_TIME}s</b>"
    )


def turn_text(game: dict):
    current = game["players"][game["turn"]]
    symbol = game["symbols"][game["turn"]]

    return (
        "<blockquote>🎲 <b>Your Move</b></blockquote>\n\n"
        f"{symbol} Current Player:\n"
        f"<a href='tg://user?id={game['turn']}'>{current['name']}</a>\n\n"
        f"⏳ Time Remaining: <b>{TURN_TIME}s</b>\n\n"
        "<i>Choose wisely, darling. ♡</i>"
    )


def move_text(player_name: str):
    return (
        "<blockquote>✨ <b>Move Recorded</b></blockquote>\n\n"
        f"<b>{player_name}</b> made a move."
    )


def timeout_text(player_name: str):
    return (
        "<blockquote>⏰ <b>Time's Up</b></blockquote>\n\n"
        f"<b>{player_name}</b> failed to move in time.\n\n"
        "<i>Fate dislikes hesitation. ♡</i>"
    )


def stop_text(player_name: str):
    return (
        "<blockquote>🛑 <b>Duel Ended</b></blockquote>\n\n"
        f"<b>{player_name}</b> stopped the match."
    )


def draw_text(game: dict):
    return (
        "<blockquote>🤝 <b>Perfect Balance</b></blockquote>\n\n"
        "<i>❝ Neither side blinked. Neither side broke. ♡ ❞</i>\n\n"
        "The duel ends in a draw.\n\n"
        f"✨ Both players receive <b>{DRAW_XP} XP</b>."
    )


def winner_text(game: dict, winner_id: int):
    winner = game["players"][winner_id]
    symbol = game["symbols"][winner_id]

    loser_id = None

    for uid in game["players"]:
        if uid != winner_id:
            loser_id = uid
            break

    loser = game["players"][loser_id]

    return (
        "<blockquote>🏆 <b>Duel Winner</b></blockquote>\n\n"
        "<i>❝ Ahahaha~ What a beautiful victory. ♡ ❞</i>\n\n"
        f"{symbol} Champion:\n"
        f"<a href='tg://user?id={winner_id}'>{winner['name']}</a>\n\n"
        f"💔 Defeated:\n"
        f"<a href='tg://user?id={loser_id}'>{loser['name']}</a>\n\n"
        "━━━━━━━━━━━━━━\n"
        f"💰 Winner: +<b>{WIN_COINS}</b> Coins\n"
        f"✨ Winner: +<b>{WIN_XP}</b> XP\n"
        f"📉 Loser: +<b>{LOSE_XP}</b> XP\n"
        "━━━━━━━━━━━━━━"
    )


def rules_text():
    return (
        "<blockquote>♟ <b>Tic Tac Toe Rules</b></blockquote>\n\n"
        "🎯 Get 3 symbols in a row.\n"
        "↔ Horizontal\n"
        "↕ Vertical\n"
        "🔷 Diagonal\n\n"
        "⏳ Each player gets limited time per turn.\n"
        "🏆 Winner receives Coins and XP.\n"
        "🤝 Draw grants XP to both players.\n\n"
        "<i>Simple board. Dangerous minds. ♡</i>"
    )