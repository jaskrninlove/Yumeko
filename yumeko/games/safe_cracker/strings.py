# ==========================================================
#  Yumeko Games Bot — Safe Cracker Strings
#  Copyright (c) 2026 Jass  |  Version 2.0.0
# ==========================================================

import random

# ── Symbols used in the code ──────────────────────────────
SYMBOLS = ["🔴", "🔵", "🟡", "🟢", "🟣", "🟠"]
CODE_LENGTH = 4
MAX_GUESSES = 8


# ── Lobby ─────────────────────────────────────────────────

def lobby_text(host: str, player_list: str, count: int, timeout: int) -> str:
    openers = [
        "I've hidden something precious~  Can you crack the code before time runs out~?  ♡",
        "Ahahaha~  4 symbols~  8 guesses~  One combination~  ♡",
        "The safe is locked~  The code is mine~  Prove you're worthy~  ♡",
        "Logic~  Deduction~  Instinct~  All of them~  Together~  ♡",
        "Every guess tells you something~  If you're smart enough to read it~  ♡",
    ]
    return (
        f"<blockquote>🔐 <b>SAFE CRACKER</b></blockquote>\n\n"
        f"<i>❝ {random.choice(openers)} ❞</i>\n\n"
        f"🎴 Host: <b>{host}</b>\n\n"
        f"<b>How It Works:</b>\n"
        f"  ◈ Yumeko hides a secret <b>4-symbol code</b>\n"
        f"  ◈ Symbols: {' '.join(SYMBOLS)}\n"
        f"  ◈ Build your guess using buttons — tap to add symbols\n"
        f"  ◈ After each guess you get feedback:\n"
        f"      🟩 = correct symbol, correct position\n"
        f"      🟨 = correct symbol, wrong position\n"
        f"      ⬛ = symbol not in code\n"
        f"  ◈ <b>{MAX_GUESSES} guesses max</b> — use them wisely\n"
        f"  ◈ First to crack it wins~  ♡\n\n"
        f"👥 <b>Players ({count}):</b>\n{player_list}\n\n"
        f"⏳ <i>Auto-starts in {timeout}s...</i>"
    )


def lobby_updated(host: str, player_list: str, count: int) -> str:
    lines = [
        "Another mind enters the puzzle~  ♡",
        "Ahahaha~  More challengers~  ♡",
        "The safe grows more contested~  ♡",
    ]
    return (
        f"<blockquote>🔐 <b>SAFE CRACKER</b></blockquote>\n\n"
        f"<i>❝ {random.choice(lines)} ❞</i>\n\n"
        f"🎴 Host: <b>{host}</b>\n\n"
        f"👥 <b>Players ({count}):</b>\n{player_list}\n\n"
        f"<i>Waiting for host to lock the safe...</i>"
    )


# ── Game start ────────────────────────────────────────────

def game_start_text(count: int) -> str:
    return (
        f"<blockquote>🔐 <b>SAFE CRACKER — BEGIN!</b></blockquote>\n\n"
        f"<i>❝ The code is set~  {count} minds against one lock~  ♡ ❞</i>\n\n"
        f"Each player gets their own cracking panel~\n"
        f"Tap your symbols~  Build your guess~  Submit~\n\n"
        f"<i>May logic guide you~  ♡</i>"
    )


# ── Player panel ──────────────────────────────────────────

def panel_text(player_name: str, guesses_left: int,
               current_build: list, history: list) -> str:
    taunts_low = [
        "Running out of chances~  ♡  Think harder.",
        f"Only {guesses_left} guesses left~  Every one counts~  ♡",
        "The safe is still locked~  ♡  Concentrate.",
    ]
    taunts_high = [
        "The code waits~  ♡  Take your time.",
        "Ahahaha~  What's your next guess~?  ♡",
        "Reason it out~  ♡  You can do this.",
        "Each clue narrows it down~  ♡",
    ]
    taunt = random.choice(taunts_low if guesses_left <= 3 else taunts_high)

    build_display = " ".join(current_build) if current_build else "_ _ _ _"
    history_text  = _format_history(history)

    return (
        f"<blockquote>🔐 <b>Safe Cracker</b>  ·  <b>{player_name}</b></blockquote>\n\n"
        f"<i>❝ {taunt} ❞</i>\n\n"
        f"🔢 Guesses left: <b>{guesses_left}</b>\n\n"
        f"<b>Your Guess:</b>  {build_display}\n\n"
        + (f"<b>History:</b>\n{history_text}\n\n" if history_text else "")
        + f"<i>Tap symbols below to build~  then Submit~  ♡</i>"
    )


def _format_history(history: list) -> str:
    """history = list of (guess_symbols, bulls, cows)"""
    lines = []
    for guess, bulls, cows in history:
        guess_str    = " ".join(guess)
        feedback_str = "🟩" * bulls + "🟨" * cows + "⬛" * (CODE_LENGTH - bulls - cows)
        lines.append(f"  {guess_str}  →  {feedback_str}")
    return "\n".join(lines)


# ── Feedback ──────────────────────────────────────────────

def guess_feedback(name: str, guess: list, bulls: int, cows: int,
                   guesses_left: int) -> str:
    guess_str    = " ".join(guess)
    feedback_str = "🟩" * bulls + "🟨" * cows + "⬛" * (CODE_LENGTH - bulls - cows)

    if bulls == CODE_LENGTH:
        return ""  # handled by win

    reactions_cold = [
        f"<b>{name}</b>~  Not close~  ♡  Try again.",
        f"Ahahaha~  <b>{name}</b>~  Think harder~  ♡",
    ]
    reactions_warm = [
        f"<b>{name}</b>~  Getting warmer~  ♡",
        f"Ahahaha~  <b>{name}</b>~  Something is right~  ♡",
    ]
    reactions_hot = [
        f"<b>{name}</b>~  Very close~  ♡  Don't waste it.",
        f"Ahahaha~  <b>{name}</b>~  Almost there~  ♡",
    ]

    if bulls + cows == 0:
        reaction = random.choice(reactions_cold)
    elif bulls >= 2:
        reaction = random.choice(reactions_hot)
    else:
        reaction = random.choice(reactions_warm)

    return (
        f"<i>❝ {reaction} ❞</i>\n"
        f"{guess_str}  →  <b>{feedback_str}</b>\n"
        f"🟩 {bulls} correct  ·  🟨 {cows} misplaced\n"
        f"Guesses left: <b>{guesses_left}</b>"
    )


def eliminated_text(name: str, code: list) -> str:
    msgs = [
        f"💀 <b>{name}</b> used all {MAX_GUESSES} guesses~  ♡  The safe stays locked.",
        f"💀 Ahahaha~  <b>{name}</b>~  {MAX_GUESSES} attempts and still nothing~  ♡",
        f"💀 <b>{name}</b>~  The code was too much~  ♡",
    ]
    code_str = " ".join(code)
    return random.choice(msgs) + f"\n<i>The code was: {code_str}</i>"


# ── Victory ───────────────────────────────────────────────

def victory_text(winner: str, code: list, guesses_used: int,
                 coins: int, xp: int, loser_xp: int) -> str:
    code_str = " ".join(code)
    closes   = [
        f"<b>{winner}</b>~  You cracked my safe~  ♡  Magnificent.",
        f"Ahahaha~  <b>{winner}</b>~  That mind is dangerous~  ♡",
        f"<b>{winner}</b>~  {guesses_used} guesses~  The code surrendered to you~  ♡",
        f"Incredible~  <b>{winner}</b> cracked it in <b>{guesses_used}</b>~  ♡",
    ]
    speed_badge = ""
    if guesses_used <= 3:
        speed_badge = "💎 <b>GENIUS CRACK — 3 or fewer guesses!</b>\n\n"
    elif guesses_used <= 5:
        speed_badge = "🔥 <b>SHARP MIND — 5 or fewer guesses!</b>\n\n"

    return (
        f"<blockquote>🏆 <b>SAFE CRACKER — CRACKED!</b></blockquote>\n\n"
        f"{speed_badge}"
        f"<i>❝ {random.choice(closes)} ❞</i>\n\n"
        f"👑 <b>{winner}</b>\n"
        f"🔢 Guesses used: <b>{guesses_used} / {MAX_GUESSES}</b>\n"
        f"🔐 Code was: {code_str}\n\n"
        f"💰 +<b>{coins}</b> coins  ·  ✨ +<b>{xp}</b> XP\n"
        f"<i>Others: +{loser_xp} XP for trying~  ♡</i>"
    )


def no_winner_text(code: list) -> str:
    code_str = " ".join(code)
    return (
        f"<blockquote>🔐 <b>Safe Remains Locked</b></blockquote>\n\n"
        f"<i>❝ Nobody cracked it~  ♡  The safe is mine~  Always was~  ♡ ❞</i>\n\n"
        f"The code was: <b>{code_str}</b>"
    )


# ── Misc ──────────────────────────────────────────────────

ALREADY_RUNNING = "🔐 <i>A Safe Cracker game is already running~  Join it!</i>"
NOT_ENOUGH      = "<i>❝ Need at least <b>1 player</b>~  ♡ ❞</i>"
GAME_CANCELLED  = (
    "<blockquote>❌ <b>Game Cancelled</b></blockquote>\n\n"
    "<i>❝ The safe stays locked~  Forever~  ♡ ❞</i>"
)
ALREADY_JOINED  = "<i>❝ Already in~  ♡ ❞</i>"
GAME_FULL       = "<i>❝ Full~  10 players max~  ♡ ❞</i>"
HOST_ONLY       = "<i>❝ Hosts only~  ♡ ❞</i>"
NOT_IN_GAME     = "<i>❝ You're not a cracker~  ♡ ❞</i>"
ALREADY_DONE    = "<i>❝ You're already done~  ♡ ❞</i>"
NEED_4_SYMBOLS  = "<i>❝ Build a full 4-symbol guess first~  ♡ ❞</i>"
GROUPS_ONLY     = "<i>❝ This game belongs in groups~  ♡ ❞</i>"