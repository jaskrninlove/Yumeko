# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
# ==========================================================

import random

from yumeko.games.rps.game import (
    WINNER_COINS,
    WINNER_XP,
    LOSER_XP,
    DRAW_XP,
    RPS_TIMEOUT,
    CHOICES,
)


def challenge_text(challenger: str, target: str):
    return (
        f"<blockquote>✂️ <b>ROCK PAPER SCISSORS</b></blockquote>\n\n"
        f"<i>❝ {random.choice(['A tiny duel of fate~', 'One hand. One choice. One thrill.', 'Let us see who fate favors, darling.'])} ❞</i>\n\n"
        f"🎴 <b>{challenger}</b> challenged <b>{target}</b>.\n\n"
        f"<b>{target}</b>, accept the duel?\n\n"
        f"⏳ Challenge expires in <b>{RPS_TIMEOUT}s</b>."
    )


def accepted_text(challenger: str, target: str):
    return (
        f"<blockquote>🎲 <b>Duel Accepted</b></blockquote>\n\n"
        f"<i>❝ Choose carefully. Even simple games can betray you. ♡ ❞</i>\n\n"
        f"Players:\n"
        f"  ◈ <b>{challenger}</b>\n"
        f"  ◈ <b>{target}</b>\n\n"
        f"Pick your move below."
    )


def chosen_popup():
    return random.choice(
        [
            "Choice locked. Yumeko saw it~",
            "Your hand has been played, darling.",
            "Interesting choice~",
            "Locked. No regrets now.",
        ]
    )


def waiting_text(game: dict):
    chosen = len(game["choices"])
    return (
        f"<blockquote>🎭 <b>Waiting For Choices</b></blockquote>\n\n"
        f"<i>❝ The table is quiet... but tension is delicious. ❞</i>\n\n"
        f"Choices locked: <b>{chosen}/2</b>"
    )


def result_text(game: dict, result: dict):
    c_choice = CHOICES[result["challenger_choice"]]
    t_choice = CHOICES[result["target_choice"]]

    if result["result"] == "draw":
        return (
            f"<blockquote>🤝 <b>DRAW</b></blockquote>\n\n"
            f"<i>❝ Ahahaha~ same choice? How perfectly boring. ❞</i>\n\n"
            f"<b>{game['challenger_name']}</b>: {c_choice}\n"
            f"<b>{game['target_name']}</b>: {t_choice}\n\n"
            f"✨ Both players get <b>{DRAW_XP}</b> XP."
        )

    return (
        f"<blockquote>🏆 <b>RPS Winner</b></blockquote>\n\n"
        f"<i>❝ Fate smiled at <b>{result['winner_name']}</b> today. ♡ ❞</i>\n\n"
        f"<b>{game['challenger_name']}</b>: {c_choice}\n"
        f"<b>{game['target_name']}</b>: {t_choice}\n\n"
        f"👑 Winner: <b>{result['winner_name']}</b>\n\n"
        f"💰 +<b>{WINNER_COINS}</b> coins\n"
        f"✨ +<b>{WINNER_XP}</b> XP\n"
        f"📉 Loser gets +<b>{LOSER_XP}</b> XP for daring to play~"
    )


def declined_text(target: str):
    return (
        f"<blockquote>❌ <b>Duel Declined</b></blockquote>\n\n"
        f"<i>❝ <b>{target}</b> walked away from the table. How cautious~ ❞</i>"
    )


def timeout_text():
    return (
        f"<blockquote>⌛ <b>Duel Expired</b></blockquote>\n\n"
        f"<i>❝ No choice was made. The thrill faded away. ❞</i>"
    )