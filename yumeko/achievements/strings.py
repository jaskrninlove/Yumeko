# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
# ==========================================================

from yumeko.achievements.badges import BADGES


def achievements_text(user_badges: list | None = None):
    user_badges = user_badges or []

    lines = []

    for badge_id, badge in BADGES.items():
        status = "✅" if badge_id in user_badges else "🔒"
        lines.append(
            f"{status} <b>{badge['name']}</b>\n"
            f"   <i>{badge['desc']}</i>"
        )

    return (
        "<blockquote>🎖 <b>Yumeko Achievements</b></blockquote>\n\n"
        "<i>❝ Every badge is proof that you dared to play. ♡ ❞</i>\n\n"
        + "\n\n".join(lines)
    )


def my_badges_text(name: str, badge_ids: list):
    if not badge_ids:
        return (
            "<blockquote>🏅 <b>My Badges</b></blockquote>\n\n"
            f"<b>{name}</b>, you have no badges yet.\n\n"
            "<i>❝ Empty hands today... legendary hands tomorrow. ♡ ❞</i>"
        )

    lines = []

    for badge_id in badge_ids:
        badge = BADGES.get(badge_id)
        if badge:
            lines.append(f"◈ <b>{badge['name']}</b>\n   <i>{badge['desc']}</i>")

    return (
        "<blockquote>🏅 <b>My Badges</b></blockquote>\n\n"
        f"👤 Player: <b>{name}</b>\n"
        f"🎖 Total Badges: <b>{len(lines)}</b>\n\n"
        + "\n\n".join(lines)
        + "\n\n<i>❝ Your story is starting to look dangerous. ♡ ❞</i>"
    )


def badge_unlocked_text(badge_name: str):
    return (
        "<blockquote>🏆 <b>Achievement Unlocked!</b></blockquote>\n\n"
        f"You unlocked: <b>{badge_name}</b>\n\n"
        "<i>❝ Ahahaha~ another mark of greatness. ♡ ❞</i>"
    )