# ==========================================================
#  Yumeko Games Bot — Hot Potato Strings
#  Copyright (c) 2026 Jass  |  Version 2.0.0
# ==========================================================

import random

def lobby_text(host: str, player_list: str, count: int, timeout: int) -> str:
    openers = [
        "Someone is going to get burned~  ♡  Will it be you?",
        "Ahahaha~  The potato doesn't care who's popular here.",
        "Pass it~  Pass it fast~  Or face the heat~  ♡",
        "One potato~  Many hands~  One loser~  ♡",
    ]
    return (
        f"<blockquote>🥔 <b>HOT POTATO</b></blockquote>\n\n"
        f"<i>❝ {random.choice(openers)} ❞</i>\n\n"
        f"🎴 Host: <b>{host}</b>\n\n"
        f"<b>How It Works:</b>\n"
        f"  ◈ The potato starts with a random player\n"
        f"  ◈ Tap <b>🥔 Pass It!</b> to throw it to someone random\n"
        f"  ◈ A hidden timer ticks~  When it explodes — whoever holds it <b>loses a life</b>\n"
        f"  ◈ 3 lives each. Lose all 3 — eliminated\n"
        f"  ◈ Last player standing wins\n\n"
        f"👥 <b>Players ({count}):</b>\n{player_list}\n\n"
        f"⏳ <i>Auto-starts in {timeout}s...</i>"
    )

def potato_holder_text(holder_name: str, pass_count: int, lives: dict) -> str:
    taunts = [
        f"<b>{holder_name}</b> is holding it~  Pass it~  PASS IT~  ♡",
        f"Ahahaha~  <b>{holder_name}</b>'s hands must be burning~  ♡",
        f"<b>{holder_name}</b>~  That thing is going to explode~  ♡",
        f"The potato belongs to <b>{holder_name}</b> now~  For how long~?",
    ]
    lives_text = "  ".join(f"<b>{name}</b>: {'❤️' * v}{'🖤' * (3-v)}"
                           for name, v in lives.items())
    return (
        f"<blockquote>🥔 <b>HOT POTATO</b></blockquote>\n\n"
        f"<i>❝ {random.choice(taunts)} ❞</i>\n\n"
        f"🔄 Passes: <b>{pass_count}</b>\n\n"
        f"❤️ <b>Lives:</b>\n{lives_text}"
    )

def pass_button(holder_name: str) -> str:
    return f"🥔 {holder_name} — PASS IT!"

def explosion_text(holder_name: str, lives_left: int) -> str:
    if lives_left > 0:
        msgs = [
            f"💥 <b>BOOM!</b>  <b>{holder_name}</b> was holding it~  -{1} life~  ♡  <b>{lives_left} left.</b>",
            f"💥 The potato exploded in <b>{holder_name}</b>'s hands~  <b>{lives_left} lives remaining.</b>",
        ]
    else:
        msgs = [
            f"💥 <b>ELIMINATED!</b>  <b>{holder_name}</b> ran out of lives~  ♡  Goodbye~",
            f"💥 <b>{holder_name}</b>~  No more lives~  You're done~  ♡",
        ]
    return f"<blockquote>{random.choice(msgs)}</blockquote>"

def passed_text(from_name: str, to_name: str) -> str:
    taunts = [
        f"<b>{from_name}</b> threw it to <b>{to_name}</b>~  ♡  Run~",
        f"<b>{to_name}</b> now has it~  Thanks to <b>{from_name}</b>~  ♡",
        f"<b>{from_name}</b> escaped~  <b>{to_name}</b> is not so lucky~",
    ]
    return f"<i>❝ {random.choice(taunts)} ❞</i>"

def victory_text(winner: str, rounds: int, coins: int, xp: int) -> str:
    return (
        f"<blockquote>🏆 <b>HOT POTATO — WINNER!</b></blockquote>\n\n"
        f"<i>❝ <b>{winner}</b> never got burned~  ♡  Remarkable. ❞</i>\n\n"
        f"👑 <b>{winner}</b>\n"
        f"🔄 Total passes: <b>{rounds}</b>\n\n"
        f"💰 +<b>{coins}</b> coins  ·  ✨ +<b>{xp}</b> XP"
    )

ALREADY_RUNNING  = "🥔 <i>A potato is already flying around in this group~  Join it!</i>"
NOT_ENOUGH       = "<i>❝ Need at least <b>3 players</b> to start Hot Potato~  ♡ ❞</i>"
GAME_CANCELLED   = "<blockquote>❌ <b>Game Cancelled</b></blockquote>\n\n<i>❝ The potato was safely disposed of~  How boring. ❞</i>"
NOT_YOUR_POTATO  = "<i>❝ You don't have the potato~  Someone else is suffering right now~  ♡ ❞</i>"
ALREADY_JOINED   = "<i>❝ You're already in~  ♡ ❞</i>"
GAME_FULL        = "<i>❝ Full~  20 players max~  Watch from safety. ❞</i>"
HOST_ONLY        = "<i>❝ Only the host can do that~  ♡ ❞</i>"