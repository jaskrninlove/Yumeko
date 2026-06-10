# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
# ==========================================================

from yumeko.social.marriage_db import days_together, remaining_time


def proposal_text(user: str, target: str):
    return (
        f"<blockquote>💌 <b>Marriage Proposal</b></blockquote>\n\n"
        f"🎭 <b>{user}</b> has placed their heart on the table.\n\n"
        f"<i>❝ Ahahaha~ a dangerous gamble of love. ♡ ❞</i>\n\n"
        f"Will <b>{target}</b> accept this proposal?"
    )


def accepted_text(user: str, target: str):
    return (
        f"<blockquote>💍 <b>Marriage Registered</b></blockquote>\n\n"
        f"🎊 <b>{user}</b> and <b>{target}</b> are now officially married in Yumeko Arcade.\n\n"
        f"<i>❝ From this moment onward, your hearts are bound by fate. ♡ ❞</i>"
    )


def rejected_text(target: str):
    return (
        f"<blockquote>💔 <b>Proposal Rejected</b></blockquote>\n\n"
        f"<i>❝ Ahahaha~ <b>{target}</b> walked away from the gamble. ❞</i>"
    )


def already_married_text():
    return (
        f"<blockquote>💍 <b>Already Married</b></blockquote>\n\n"
        f"<i>❝ No cheating at my table, darling. Divorce first. ♡ ❞</i>"
    )


def no_target_text(cmd: str):
    return (
        f"<blockquote>💌 <b>Usage</b></blockquote>\n\n"
        f"Reply to someone with <code>/{cmd}</code>."
    )


def divorce_confirm_text(name: str):
    return (
        f"<blockquote>💔 <b>Confirm Divorce</b></blockquote>\n\n"
        f"<b>{name}</b>, are you sure?\n\n"
        f"<i>❝ Some stories end quietly. Some end with a final card. ❞</i>"
    )


def divorce_done_text(user1: str, user2: str):
    return (
        f"<blockquote>💔 <b>Marriage Ended</b></blockquote>\n\n"
        f"<b>{user1}</b> and <b>{user2}</b> have chosen different paths.\n\n"
        f"<i>❝ The ring is gone... but the memory remains. ❞</i>"
    )


def spouse_text(marriage: dict, rank: int | None = None):
    u1 = marriage["user1"]["name"]
    u2 = marriage["user2"]["name"]
    love = marriage.get("love_points", 0)
    rank_text = f"#{rank}" if rank else "Unranked"

    return (
        f"<blockquote>💕 <b>Couple Profile</b></blockquote>\n\n"
        f"💍 <b>{u1}</b> × <b>{u2}</b>\n\n"
        f"📅 Together: <b>{days_together(marriage.get('married_at'))}</b> days\n"
        f"💞 Love Points: <b>{love}</b>\n"
        f"🏆 Couple Rank: <b>{rank_text}</b>\n\n"
        f"<i>❝ A bond written into Yumeko's little book of fate. ♡ ❞</i>"
    )


def no_spouse_text():
    return (
        f"<blockquote>🥀 <b>No Marriage Found</b></blockquote>\n\n"
        f"<i>❝ Your ring finger is still free, darling. ❞</i>"
    )


def love_claimed_text(marriage: dict, points: int):
    return (
        f"<blockquote>💖 <b>Daily Love Claimed</b></blockquote>\n\n"
        f"💍 <b>{marriage['user1']['name']}</b> × <b>{marriage['user2']['name']}</b>\n\n"
        f"💕 Love Points: +<b>{points}</b>\n"
        f"💞 Total Love: <b>{marriage.get('love_points', 0)}</b>\n\n"
        f"<i>❝ Every day together makes the bond stronger. ♡ ❞</i>"
    )


def love_cooldown_text(remaining: str):
    return (
        f"<blockquote>⏳ <b>Love Already Claimed</b></blockquote>\n\n"
        f"Come back in: <b>{remaining}</b>\n\n"
        f"<i>❝ Love grows slowly, darling. ♡ ❞</i>"
    )


def top_couples_text(couples: list):
    if not couples:
        return (
            f"<blockquote>🏆 <b>Top Couples</b></blockquote>\n\n"
            f"<i>❝ No legendary romances yet, darling. ❞</i>"
        )

    medals = ["🥇", "🥈", "🥉"]
    lines = []

    for i, couple in enumerate(couples, start=1):
        icon = medals[i - 1] if i <= 3 else f"{i}."
        lines.append(
            f"{icon} <b>{couple['user1']['name']}</b> × "
            f"<b>{couple['user2']['name']}</b> — "
            f"<code>{couple.get('love_points', 0)}</code> ❤️"
        )

    return (
        f"<blockquote>🏆 <b>Top Couples</b></blockquote>\n\n"
        f"{chr(10).join(lines)}\n\n"
        f"<i>❝ The most legendary romances in Yumeko Arcade. ♡ ❞</i>"
    )


def daily_couple_text(user1: str, user2: str):
    return (
        f"<blockquote>💘 <b>Couple Of The Day</b></blockquote>\n\n"
        f"🎭 Yumeko has chosen today's lucky pair.\n\n"
        f"💖 <b>{user1}</b> × <b>{user2}</b>\n\n"
        f"<i>❝ Whether fate planned it or not... today you belong together. ♡ ❞</i>\n\n"
        f"⏳ Valid for <b>24 hours</b>."
    )


def existing_daily_couple_text(doc: dict):
    return (
        f"<blockquote>💞 <b>Today's Couple Already Exists</b></blockquote>\n\n"
        f"💖 <b>{doc['user1']['name']}</b> × <b>{doc['user2']['name']}</b>\n\n"
        f"⏳ Remaining: <b>{remaining_time(doc.get('expires_at'))}</b>\n\n"
        f"<i>❝ Don't be greedy, darling. One romance per day is enough. ♡ ❞</i>"
    )