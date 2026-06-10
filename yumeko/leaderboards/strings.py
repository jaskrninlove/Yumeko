# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
#
#  Developer  : Jass
#  Project    : Yumeko Games Bot
#  Version    : 1.0.0
# ==========================================================


def leaderboard_menu_text():
    return (
        "<blockquote>🏆 <b>Yumeko Leaderboards</b></blockquote>\n\n"
        "<i>❝ The throne remembers every victory, every coin, and every beautiful risk. ♡ ❞</i>\n\n"
        "<b>Use:</b>\n"
        "<code>/leaderboard coins</code>\n"
        "<code>/leaderboard xp</code>\n"
        "<code>/leaderboard wins</code>\n"
        "<code>/leaderboard couples</code>\n"
        "<code>/leaderboard mafia</code>\n"
        "<code>/leaderboard reaction</code>\n\n"
        "Short command:\n"
        "<code>/lb coins</code>"
    )


def empty_board_text(title: str):
    return (
        f"<blockquote>{title}</blockquote>\n\n"
        "<i>❝ No legends have appeared here yet, darling. ❞</i>"
    )


def board_text(title: str, rows: list, footer: str = ""):
    if not rows:
        return empty_board_text(title)

    medals = ["🥇", "🥈", "🥉"]
    lines = []

    for i, row in enumerate(rows, start=1):
        icon = medals[i - 1] if i <= 3 else f"{i}."
        lines.append(f"{icon} {row}")

    footer_text = f"\n\n{footer}" if footer else ""

    return (
        f"<blockquote>{title}</blockquote>\n\n"
        + "\n".join(lines)
        + footer_text
        + "\n\n<i>❝ Climb higher, darling. The top is lonely but beautiful. ♡ ❞</i>"
    )


def unknown_board_text():
    return (
        "<blockquote>❌ <b>Unknown Leaderboard</b></blockquote>\n\n"
        "Available boards:\n"
        "<code>coins</code>, <code>xp</code>, <code>wins</code>, "
        "<code>couples</code>, <code>mafia</code>, <code>reaction</code>"
    )