# ==========================================================
#  Yumeko Games Bot — Number Bomb Strings
#  Copyright (c) 2026 Jass  |  Version 2.0.0
# ==========================================================

import random

# ── Lobby ─────────────────────────────────────────────────

def lobby_text(host: str, player_list: str, count: int, timeout: int) -> str:
    openers = [
        "Ahahaha~  A bomb is being prepared.  ♡",
        "One number will destroy everything.  Which one~?  ♡",
        "Count carefully, darling.  One wrong word and you're done.",
        "The bomb doesn't care who you are.  It only cares about the number.  ♡",
    ]
    return (
        f"<blockquote>💣 <b>NUMBER BOMB</b></blockquote>\n\n"
        f"<i>❝ {random.choice(openers)} ❞</i>\n\n"
        f"🎴 Host: <b>{host}</b>\n\n"
        f"<b>How It Works:</b>\n"
        f"  ◈ Players count up in turns — 1, 2, 3...\n"
        f"  ◈ A secret bomb number is hidden somewhere\n"
        f"  ◈ Whoever says it — <b>EXPLODES</b> and is eliminated\n"
        f"  ◈ Last player standing wins\n"
        f"  ◈ You have <b>15 seconds</b> per turn or you're eliminated\n\n"
        f"👥 <b>Players ({count}):</b>\n{player_list}\n\n"
        f"⏳ <i>Auto-starts in {timeout}s...</i>"
    )

def lobby_updated(host: str, player_list: str, count: int) -> str:
    joins = [
        "Another soul drawn to the countdown~  ♡",
        "Ahahaha~  The table fills.  Wonderful.",
        "More players~  More explosions~  ♡",
    ]
    return (
        f"<blockquote>💣 <b>NUMBER BOMB</b></blockquote>\n\n"
        f"<i>❝ {random.choice(joins)} ❞</i>\n\n"
        f"🎴 Host: <b>{host}</b>\n"
        f"👥 <b>Players ({count}):</b>\n{player_list}\n\n"
        f"<i>Waiting for host to arm the bomb...</i>"
    )

# ── Game Start ────────────────────────────────────────────

def game_start_text(player_list: str, count: int, bomb_range: str) -> str:
    return (
        f"<blockquote>💣 <b>THE BOMB IS ARMED!</b></blockquote>\n\n"
        f"<i>❝ Somewhere between those numbers~  lies your destruction.  ♡ ❞</i>\n\n"
        f"👥 <b>{count} players</b> competing\n"
        f"🔢 Range: <b>{bomb_range}</b>\n"
        f"⏱️ <b>15 seconds</b> per turn\n\n"
        f"{player_list}\n\n"
        f"<i>Ready~?  Then let the countdown begin.</i>"
    )

# ── Turn Prompt ───────────────────────────────────────────

def turn_prompt(player_name: str, current_number: int, seconds: int) -> str:
    taunts = [
        f"Your move, <b>{player_name}</b>~  ♡",
        f"<b>{player_name}</b>~  The number awaits you.",
        f"Ahahaha~  <b>{player_name}</b>~  Don't keep us waiting.",
        f"<b>{player_name}</b>~  Is this the one~?",
        f"Your turn, <b>{player_name}</b>~  Choose wisely.",
    ]
    return (
        f"<blockquote>🔢 <b>TURN</b></blockquote>\n\n"
        f"<i>❝ {random.choice(taunts)} ❞</i>\n\n"
        f"Last number: <b>{current_number}</b>\n"
        f"Say: <b>{current_number + 1}</b>\n"
        f"⏱️ <b>{seconds}s</b> remaining"
    )

# ── Wrong Number ──────────────────────────────────────────

def wrong_number(player_name: str, said: int, expected: int) -> str:
    return (
        f"<blockquote>❌ <b>Wrong Number!</b></blockquote>\n\n"
        f"<i>❝ <b>{player_name}</b> said <code>{said}</code>~  but we needed <code>{expected}</code>.  Eliminated~  ♡ ❞</i>"
    )

def timeout_elimination(player_name: str) -> str:
    shames = [
        f"<b>{player_name}</b> froze~  Time ran out.  Gone~  ♡",
        f"<b>{player_name}</b> couldn't count fast enough~  Eliminated.",
        f"15 seconds~  and <b>{player_name}</b> wasted them all.  Bye~  ♡",
    ]
    return (
        f"<blockquote>⌛ <b>TIMEOUT</b></blockquote>\n\n"
        f"<i>❝ {random.choice(shames)} ❞</i>"
    )

# ── Explosion ─────────────────────────────────────────────

def explosion_text(player_name: str, bomb_number: int, survivors: list) -> str:
    survivor_text = ", ".join(f"<b>{s}</b>" for s in survivors) if survivors else "—"
    bangs = [
        "BOOM~  ♡  The bomb found its victim.",
        "Ahahaha~  KABOOM~  ♡  I love this game.",
        "EXPLOSION~  ♡  Magnificent.",
        "The bomb didn't lie~  ♡  BOOM.",
    ]
    return (
        f"<blockquote>💥 <b>EXPLOSION!</b></blockquote>\n\n"
        f"<i>❝ {random.choice(bangs)} ❞</i>\n\n"
        f"💣 <b>{player_name}</b> said the bomb number: <code>{bomb_number}</code>\n\n"
        f"🏃 <b>Survivors:</b> {survivor_text}"
    )

# ── Victory ───────────────────────────────────────────────

def victory_text(winner: str, total_numbers: int, coins: int, xp: int, loser_xp: int) -> str:
    closes = [
        f"<b>{winner}</b> survived the entire countdown~  ♡  Magnificent.",
        f"Ahahaha~  <b>{winner}</b> is still standing~  ♡  The last one.",
        f"<b>{winner}</b>~  You counted your way to victory.  Beautiful.",
    ]
    return (
        f"<blockquote>🏆 <b>NUMBER BOMB — WINNER!</b></blockquote>\n\n"
        f"<i>❝ {random.choice(closes)} ❞</i>\n\n"
        f"👑 <b>{winner}</b>\n"
        f"🔢 Numbers counted: <b>{total_numbers}</b>\n\n"
        f"💰 +<b>{coins}</b> coins  ·  ✨ +<b>{xp}</b> XP\n"
        f"<i>Others: +{loser_xp} XP for surviving as long as you did~</i>"
    )

def no_winner_text() -> str:
    return (
        f"<blockquote>💀 <b>Everyone Exploded~</b></blockquote>\n\n"
        f"<i>❝ Ahahaha~  The bomb took everyone.  No survivors.  Wonderful~  ♡ ❞</i>"
    )

# ── Misc ──────────────────────────────────────────────────

NOT_IN_GAME  = "<i>❝ You're not in this game~  Watch quietly from the sidelines. ❞</i>"
NOT_YOUR_TURN = "<i>❝ Patience~  ♡  It's not your turn yet. ❞</i>"
ALREADY_RUNNING = "💣 <i>A Number Bomb is already ticking in this group~  Join it!</i>"
GAME_CANCELLED = (
    "<blockquote>❌ <b>Game Cancelled</b></blockquote>\n\n"
    "<i>❝ The bomb was defused~  How anticlimactic. ❞</i>"
)
NOT_ENOUGH_PLAYERS = "<i>❝ Need at least <b>2 brave souls</b> to start~  ♡ ❞</i>"
ALREADY_JOINED = "<i>❝ You're already in~  Sit tight and count your breaths. ❞</i>"
GAME_FULL = "<i>❝ The table is full~  Watch from safety. ❞</i>"
HOST_ONLY = "<i>❝ Only the host controls the bomb~  ♡ ❞</i>"
GROUPS_ONLY = "<i>❝ This chaos belongs in groups, not private chats~  ♡ ❞</i>"