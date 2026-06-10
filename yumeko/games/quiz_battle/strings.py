# ==========================================================
#  Yumeko Games Bot — Quiz Battle Strings
#  Copyright (c) 2026 Jass  |  Version 2.0.0
# ==========================================================

import random

def lobby_text(host: str, player_list: str, count: int, timeout: int) -> str:
    openers = [
        "Knowledge is power~  But speed is everything~  ♡",
        "Ahahaha~  Let's see how fast that brain of yours really is~  ♡",
        "Ten questions~  One winner~  Zero mercy~  ♡",
        "The smartest player doesn't always win~  The fastest one does~  ♡",
    ]
    return (
        f"<blockquote>🧠 <b>QUIZ BATTLE</b></blockquote>\n\n"
        f"<i>❝ {random.choice(openers)} ❞</i>\n\n"
        f"🎴 Host: <b>{host}</b>\n\n"
        f"<b>How It Works:</b>\n"
        f"  ◈ <b>10 rounds</b> of questions\n"
        f"  ◈ First correct answer wins the round — <b>+3 points</b>\n"
        f"  ◈ 2nd correct — <b>+1 point</b>\n"
        f"  ◈ Wrong answer — <b>-1 point</b> penalty\n"
        f"  ◈ <b>Speed bonus</b> — answer in under 5s for +1 extra\n"
        f"  ◈ Most points after 10 rounds wins\n\n"
        f"👥 <b>Players ({count}):</b>\n{player_list}\n\n"
        f"⏳ <i>Auto-starts in {timeout}s...</i>"
    )

def question_text(round_num: int, total: int, category: str, question: str,
                  options: list, seconds: int) -> str:
    option_labels = ["🅰️", "🅱️", "🇨", "🇩"]
    option_lines  = "\n".join(f"  {option_labels[i]} {opt}"
                              for i, opt in enumerate(options))
    taunts = [
        "Think fast~  ♡",
        "Ahahaha~  Do you know this one~?",
        "The clock is ticking~  ♡",
        "First one in~  wins the round~  ♡",
        "Don't overthink it~  Or do~  ♡",
    ]
    return (
        f"<blockquote>🧠 <b>Round {round_num} / {total}</b>  ·  {category}</blockquote>\n\n"
        f"<i>❝ {random.choice(taunts)} ❞</i>\n\n"
        f"<b>{question}</b>\n\n"
        f"{option_lines}\n\n"
        f"⏱️ <b>{seconds}s</b> to answer"
    )

def correct_first(player: str, answer: str, time_ms: int, bonus: bool) -> str:
    speed_note = "  ⚡ <b>Speed Bonus!</b>" if bonus else ""
    praises = [
        f"<b>{player}</b> was first~  ♡  Magnificent.",
        f"Ahahaha~  <b>{player}</b> got it!",
        f"<b>{player}</b>~  That brain works fast~  ♡",
    ]
    return (
        f"✅ {random.choice(praises)}\n"
        f"Answer: <b>{answer}</b>  ·  ⏱️ <code>{time_ms}ms</code>{speed_note}"
    )

def correct_later(player: str, points: int) -> str:
    return f"✅ <b>{player}</b> also got it~  +{points} pt"

def wrong_answer(player: str) -> str:
    taunts = [
        f"❌ <b>{player}</b>~  Wrong~  -1 point~  ♡",
        f"❌ Ahahaha~  <b>{player}</b> guessed wrong~  ♡",
        f"❌ <b>{player}</b>~  Not quite~  -1~  ♡",
    ]
    return random.choice(taunts)

def round_timeout(answer: str) -> str:
    shames = [
        f"⌛ Time's up~  Nobody got it~  The answer was <b>{answer}</b>~  ♡",
        f"⌛ Ahahaha~  All stumped~  It was <b>{answer}</b>~  ♡",
    ]
    return random.choice(shames)

def round_scoreboard(scores: dict, round_num: int, total: int) -> str:
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    medals = ["🥇","🥈","🥉"] + ["🔹"] * 20
    lines  = [f"  {medals[i]} <b>{name}</b>  —  {pts} pts"
              for i, (name, pts) in enumerate(sorted_scores)]
    return (
        f"<blockquote>📊 <b>After Round {round_num} / {total}</b></blockquote>\n\n"
        + "\n".join(lines)
    )

def victory_text(winner: str, scores: dict, total_rounds: int,
                 coins: int, xp: int) -> str:
    sorted_s = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    medals   = ["🥇","🥈","🥉"] + ["🔹"] * 20
    board    = "\n".join(f"  {medals[i]} <b>{n}</b>  —  {p} pts"
                         for i, (n, p) in enumerate(sorted_s))
    closes   = [
        f"<b>{winner}</b> dominated every round~  ♡  Unstoppable.",
        f"Ahahaha~  <b>{winner}</b> wins~  ♡  That brain is dangerous.",
        f"<b>{winner}</b>~  The quiz table bows to you~  ♡",
    ]
    return (
        f"<blockquote>🏆 <b>QUIZ BATTLE — OVER!</b></blockquote>\n\n"
        f"<i>❝ {random.choice(closes)} ❞</i>\n\n"
        f"👑 Champion: <b>{winner}</b>\n\n"
        f"📊 <b>Final Scores:</b>\n{board}\n\n"
        f"💰 +<b>{coins}</b> coins  ·  ✨ +<b>{xp}</b> XP"
    )

ALREADY_RUNNING = "🧠 <i>A Quiz Battle is already running here~  Join it!</i>"
NOT_ENOUGH      = "<i>❝ Need at least <b>2 players</b> to start~  ♡ ❞</i>"
GAME_CANCELLED  = "<blockquote>❌ <b>Quiz Cancelled</b></blockquote>\n\n<i>❝ The questions go unanswered~  Disappointing. ❞</i>"
ALREADY_JOINED  = "<i>❝ You're already in~  ♡ ❞</i>"
GAME_FULL       = "<i>❝ Full~  20 players max. ❞</i>"
HOST_ONLY       = "<i>❝ Hosts only~  ♡ ❞</i>"
GROUPS_ONLY     = "<i>❝ Quiz Battle is a group game~  ♡ ❞</i>"