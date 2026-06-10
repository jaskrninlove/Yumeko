# ==========================================================
#  Yumeko Games Bot — Minesweeper Strings
#  Copyright (c) 2026 Jass  |  Version 2.0.0
# ==========================================================

import random

# ── Lobby ─────────────────────────────────────────────────

def lobby_text(host: str, player_list: str, count: int,
               timeout: int, mode: str) -> str:
    openers = [
        "Every square hides a secret~  Some are beautiful~  Some will kill you~  ♡",
        "Ahahaha~  Tap carefully~  The mines don't care how brave you are~  ♡",
        "One wrong tap and it's all over~  How deliciously tense~  ♡",
        "The field looks innocent~  It isn't~  ♡",
        "Somewhere under those squares~  destruction waits patiently~  ♡",
    ]
    mode_desc = {
        "solo":  "🎯 Solo Mode — beat your own record",
        "coop":  "🤝 Co-op Mode — survive together",
        "rival": "⚔️ Rival Mode — whoever survives longest wins",
    }
    return (
        f"<blockquote>💎 <b>MINESWEEPER</b></blockquote>\n\n"
        f"<i>❝ {random.choice(openers)} ❞</i>\n\n"
        f"🎴 Host: <b>{host}</b>\n"
        f"🎮 Mode: {mode_desc.get(mode, mode_desc['rival'])}\n\n"
        f"<b>How It Works:</b>\n"
        f"  ◈ A hidden minefield is generated\n"
        f"  ◈ Tap squares to reveal them via buttons\n"
        f"  ◈ Numbers show nearby mine count\n"
        f"  ◈ Hit a mine — <b>eliminated</b>~  ♡\n"
        f"  ◈ Clear the most safe squares to win\n"
        f"  ◈ Flag suspected mines to protect yourself\n\n"
        f"👥 <b>Players ({count}):</b>\n{player_list}\n\n"
        f"⏳ <i>Auto-starts in {timeout}s...</i>"
    )


def lobby_updated(host: str, player_list: str, count: int, mode: str) -> str:
    lines = [
        "Another soul brave enough to tap~  ♡",
        "Ahahaha~  The field grows more interesting~  ♡",
        "More players~  More explosions~  ♡",
    ]
    return (
        f"<blockquote>💎 <b>MINESWEEPER</b></blockquote>\n\n"
        f"<i>❝ {random.choice(lines)} ❞</i>\n\n"
        f"🎴 Host: <b>{host}</b>\n\n"
        f"👥 <b>Players ({count}):</b>\n{player_list}\n\n"
        f"<i>Waiting for host to start...</i>"
    )


# ── Board rendering ───────────────────────────────────────

# Emoji for revealed numbers
NUMBER_EMOJI = {
    0: "　",   # blank (safe, no mines nearby)
    1: "1️⃣",
    2: "2️⃣",
    3: "3️⃣",
    4: "4️⃣",
    5: "5️⃣",
    6: "6️⃣",
    7: "7️⃣",
    8: "8️⃣",
}

HIDDEN_EMOJI  = "🟦"
FLAG_EMOJI    = "🚩"
MINE_EMOJI    = "💥"
SAFE_EMOJI    = "🟩"
BOOM_EMOJI    = "💀"


def board_caption(player_name: str, safe_count: int, total_safe: int,
                  flags_left: int, lives: int, status: str = "playing") -> str:
    status_line = {
        "playing": f"<i>❝ Every tap could be your last~  ♡ ❞</i>",
        "won":     f"<i>❝ Ahahaha~  You survived~  ♡  Magnificent. ❞</i>",
        "dead":    f"<i>❝ BOOM~  ♡  Beautiful explosion. ❞</i>",
    }.get(status, "")

    lives_str = "❤️" * lives + "🖤" * (3 - lives)
    return (
        f"<blockquote>💎 <b>MINESWEEPER</b></blockquote>\n\n"
        f"{status_line}\n\n"
        f"👤 <b>{player_name}</b>\n"
        f"{lives_str}  ·  🚩 Flags: <b>{flags_left}</b>\n"
        f"🟩 Safe revealed: <b>{safe_count} / {total_safe}</b>"
    )


def scoreboard_text(scores: list) -> str:
    """scores = list of (name, safe_count, status)"""
    medals = ["🥇", "🥈", "🥉"] + ["🔹"] * 20
    sorted_s = sorted(scores, key=lambda x: (x[2] != "dead", x[1]), reverse=True)
    lines = []
    for i, (name, safe, status) in enumerate(sorted_s):
        tag = "💀" if status == "dead" else ("🏆" if i == 0 else "")
        lines.append(f"  {medals[i]} <b>{name}</b>  —  {safe} safe  {tag}")
    return (
        f"<blockquote>📊 <b>Scoreboard</b></blockquote>\n\n"
        + "\n".join(lines)
    )


# ── Events ────────────────────────────────────────────────

def mine_hit_text(player_name: str, row: int, col: int, lives_left: int) -> str:
    booms = [
        f"💥 <b>{player_name}</b> tapped a mine at <b>({row+1},{col+1})</b>~  ♡",
        f"💥 Ahahaha~  <b>{player_name}</b> found the mine~  ♡  Spectacular.",
        f"💥 <b>BOOM</b>~  <b>{player_name}</b> at <b>({row+1},{col+1})</b>~  ♡",
    ]
    if lives_left > 0:
        return random.choice(booms) + f"\n<b>{lives_left} lives remaining~</b>"
    return random.choice(booms) + f"\n<b>Eliminated~  ♡</b>"


def safe_tap_text(player_name: str, revealed: int) -> str:
    if revealed % 5 == 0 and revealed > 0:
        msgs = [
            f"<i>❝ {revealed} squares cleared~  <b>{player_name}</b> is daring~  ♡ ❞</i>",
            f"<i>❝ Ahahaha~  {revealed} safe~  Keep going~  ♡ ❞</i>",
        ]
        return random.choice(msgs)
    return ""


def flag_planted_text(player_name: str, row: int, col: int) -> str:
    return f"🚩 <b>{player_name}</b> flagged <b>({row+1},{col+1})</b>~"


def player_eliminated(player_name: str, safe_count: int) -> str:
    msgs = [
        f"💀 <b>{player_name}</b> has been eliminated~  ♡  They revealed <b>{safe_count}</b> safe squares.",
        f"💀 Ahahaha~  <b>{player_name}</b> is gone~  <b>{safe_count}</b> squares — not bad~  ♡",
    ]
    return random.choice(msgs)


def all_safe_cleared(player_name: str) -> str:
    msgs = [
        f"💎 <b>{player_name}</b> cleared the entire field~  ♡  Godlike.",
        f"💎 Ahahaha~  <b>{player_name}</b> found every safe square~  ♡  Magnificent.",
    ]
    return random.choice(msgs)


# ── Victory ───────────────────────────────────────────────

def victory_text(winner: str, safe_count: int, total_safe: int,
                 is_perfect: bool, coins: int, xp: int,
                 loser_xp: int, scoreboard: str) -> str:
    perfect = "💎 <b>PERFECT CLEAR!</b>\n\n" if is_perfect else ""
    closes = [
        f"<b>{winner}</b>~  You read the field like a gambler reads a table~  ♡",
        f"Ahahaha~  <b>{winner}</b> survived~  ♡  Nerve of steel.",
        f"<b>{winner}</b>~  The mines couldn't touch you~  ♡  Incredible.",
    ]
    return (
        f"<blockquote>🏆 <b>MINESWEEPER — OVER!</b></blockquote>\n\n"
        f"{perfect}"
        f"<i>❝ {random.choice(closes)} ❞</i>\n\n"
        f"👑 Champion: <b>{winner}</b>\n"
        f"🟩 Safe squares: <b>{safe_count} / {total_safe}</b>\n\n"
        f"{scoreboard}\n\n"
        f"💰 +<b>{coins}</b> coins  ·  ✨ +<b>{xp}</b> XP\n"
        f"<i>Others: +{loser_xp} XP for daring to tap~</i>"
    )


def no_winner_text() -> str:
    return (
        f"<blockquote>💥 <b>Everyone Hit a Mine!</b></blockquote>\n\n"
        f"<i>❝ Ahahaha~  The field won~  ♡  How embarrassing for everyone. ❞</i>"
    )


# ── Misc strings ──────────────────────────────────────────

ALREADY_RUNNING  = "💎 <i>A Minesweeper game is already running~  Join it!</i>"
NOT_ENOUGH       = "<i>❝ Need at least <b>1 player</b> to start~  ♡ ❞</i>"
GAME_CANCELLED   = (
    "<blockquote>❌ <b>Game Cancelled</b></blockquote>\n\n"
    "<i>❝ The mines rest undisturbed~  For now~  ♡ ❞</i>"
)
NOT_IN_GAME      = "<i>❝ You're not in this game~  Watch from safety~  ♡ ❞</i>"
NOT_YOUR_TURN    = "<i>❝ Wait your turn~  Patience~  ♡ ❞</i>"
ALREADY_DEAD     = "<i>❝ You already exploded~  Watch how others die~  ♡ ❞</i>"
ALREADY_REVEALED = "<i>❝ Already revealed~  Try another square~  ♡ ❞</i>"
ALREADY_JOINED   = "<i>❝ Already in~  ♡ ❞</i>"
GAME_FULL        = "<i>❝ Full~  20 players max~  ♡ ❞</i>"
HOST_ONLY        = "<i>❝ Hosts only~  ♡ ❞</i>"
GROUPS_ONLY      = "<i>❝ Minesweeper is a group game~  ♡ ❞</i>"