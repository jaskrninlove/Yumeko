# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
# ==========================================================

import random

from yumeko.games.blackjack.game import (
    JOIN_TIME,
    MIN_PLAYERS,
    MAX_PLAYERS,
    WIN_COINS,
    WIN_XP,
    BLACKJACK_COINS,
    BLACKJACK_XP,
    PUSH_XP,
    LOSE_XP,
    format_players,
    format_hand,
    hand_text,
    hand_value,
    format_final_rows,
)


def lobby_text(game: dict):
    return (
        f"<blockquote>🎴 <b>BLACKJACK TABLE</b></blockquote>\n\n"
        f"<i>❝ {random.choice(['Ahahaha~ cards, risk, and greed. My favorite table. ♡', 'One card can save you... or ruin everything.', 'Sit down, darling. Let fate deal.'])} ❞</i>\n\n"
        f"🎴 Host: <b>{game['host_name']}</b>\n\n"
        f"<b>How to join:</b>\n"
        f"Send <code>/join</code> or tap the button below.\n\n"
        f"<b>Table Rules:</b>\n"
        f"  ◈ {MIN_PLAYERS}–{MAX_PLAYERS} players\n"
        f"  ◈ Get close to <b>21</b> without going over\n"
        f"  ◈ <b>Hit</b> = take card\n"
        f"  ◈ <b>Stand</b> = keep hand\n"
        f"  ◈ <b>Surrender</b> = leave round safely\n"
        f"  ◈ Dealer Yumeko plays after everyone\n\n"
        f"⏳ Lobby closes in <b>{JOIN_TIME}s</b>\n\n"
        f"👥 <b>Players ({len(game['players'])}):</b>\n"
        f"{format_players(game)}"
    )


def joined_text(name: str, count: int):
    return f"🎴 <b>{name}</b> sat at the Blackjack table.\n\nPlayers now: <b>{count}</b>"


def countdown_text(seconds: int):
    return (
        f"<blockquote>🎴 <b>Blackjack Lobby</b></blockquote>\n\n"
        f"<i>❝ {seconds} seconds left. Sit before the cards are dealt. ❞</i>\n\n"
        f"Send <code>/join</code> to enter."
    )


def not_enough_text(game: dict):
    return (
        f"<blockquote>😔 <b>Blackjack Cancelled</b></blockquote>\n\n"
        f"<i>❝ Only {len(game['players'])} player joined. A lonely table is no fun. ❞</i>\n\n"
        f"At least <b>{MIN_PLAYERS}</b> players are required."
    )


def turn_text(game: dict, player: dict):
    dealer_up = game["dealer"][0]

    return (
        f"<blockquote>🎴 <b>Blackjack Turn</b></blockquote>\n\n"
        f"<i>❝ <b>{player['name']}</b>, will you take another card... or fear it? ♡ ❞</i>\n\n"
        f"👤 Player: <b>{player['name']}</b>\n"
        f"🃏 Your Hand: {format_hand(player)}\n\n"
        f"🎭 Yumeko Dealer: {dealer_up['rank']}{dealer_up['suit']} + <b>Hidden</b>\n\n"
        f"Choose your move."
    )


def blackjack_auto_text(game: dict):
    lines = []

    for user_id in game["order"]:
        p = game["players"][user_id]
        if p["result"] == "blackjack":
            lines.append(f"🖤 <b>{p['name']}</b> got Blackjack instantly!")

    if not lines:
        return ""

    return "\n".join(lines) + "\n\n"


def hit_text(player: dict):
    return (
        f"<blockquote>🃏 <b>Card Drawn</b></blockquote>\n\n"
        f"<i>❝ Another card. How greedy~ I love it. ♡ ❞</i>\n\n"
        f"👤 <b>{player['name']}</b>\n"
        f"🃏 Hand: {format_hand(player)}"
    )


def bust_text(player: dict):
    return (
        f"<blockquote>💥 <b>BUST!</b></blockquote>\n\n"
        f"<i>❝ Ahahaha~ greed swallowed <b>{player['name']}</b>. ❞</i>\n\n"
        f"🃏 Hand: {format_hand(player)}\n"
        f"<b>{player['name']}</b> is out of this round."
    )


def stand_text(player: dict):
    return (
        f"✋ <b>{player['name']}</b> stands with <b>{player['score']}</b>."
    )


def surrender_text(player: dict):
    return (
        f"🏳️ <b>{player['name']}</b> surrendered. Yumeko smiles quietly."
    )


def final_text(game: dict):
    dealer_score = hand_value(game["dealer"])

    return (
        f"<blockquote>🎭 <b>Blackjack Results</b></blockquote>\n\n"
        f"<i>❝ The dealer reveals her hand. Did fate betray you, darling? ❞</i>\n\n"
        f"🎭 <b>Yumeko Dealer:</b> {hand_text(game['dealer'])} "
        f"(<code>{dealer_score}</code>)\n\n"
        f"📜 <b>Players:</b>\n"
        f"{format_final_rows(game)}\n\n"
        f"<b>Rewards:</b>\n"
        f"🖤 Blackjack Win: +{BLACKJACK_COINS} coins · +{BLACKJACK_XP} XP\n"
        f"🏆 Win: +{WIN_COINS} coins · +{WIN_XP} XP\n"
        f"🤝 Push: +{PUSH_XP} XP\n"
        f"💀 Lose: +{LOSE_XP} XP"
    )


def rules_text():
    return (
        f"<blockquote>🎴 <b>Blackjack Rules</b></blockquote>\n\n"
        f"<b>Goal:</b>\n"
        f"Get as close as possible to <b>21</b> without going over.\n\n"
        f"<b>Card Values:</b>\n"
        f"  ◈ 2–10 = same value\n"
        f"  ◈ J, Q, K = 10\n"
        f"  ◈ A = 11 or 1 automatically\n\n"
        f"<b>Moves:</b>\n"
        f"  ◈ 🃏 <b>Hit</b> — take one more card\n"
        f"  ◈ ✋ <b>Stand</b> — keep your current hand\n"
        f"  ◈ 🏳️ <b>Surrender</b> — leave the round\n\n"
        f"<b>Results:</b>\n"
        f"  ◈ Over 21 = Bust\n"
        f"  ◈ Higher than dealer = Win\n"
        f"  ◈ Same as dealer = Push\n"
        f"  ◈ Natural 21 with first 2 cards = Blackjack\n\n"
        f"<i>❝ One more card can make you a legend... or ruin you. ♡ ❞</i>"
    )


def stopped_text():
    return (
        f"<blockquote>🛑 <b>Blackjack Stopped</b></blockquote>\n\n"
        f"<i>❝ The cards return to silence... for now. ❞</i>"
    )