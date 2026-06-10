# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
#
#  Developer  : Jass
#  Project    : Yumeko Games Bot
#  Version    : 2.0.0
#
#  GitHub     : Private
#  License    : MIT License
#
#  This file is part of Yumeko Games Bot.
#  Unauthorized removal of this notice is discouraged.
#
#  © 2026 Jass. All Rights Reserved.
# ==========================================================

# ─────────────────────────────────────────────────────────────────────────────
#  Every single string in this file is written as if Yumeko Jabami herself
#  is speaking. Charismatic. Unhinged. Elegant. Obsessed with the thrill.
#  She doesn't care about winning — she cares about the RUSH.
# ─────────────────────────────────────────────────────────────────────────────

import random


# ── Lobby / Opening ───────────────────────────────────────────────────────────

def lobby_text(host_name: str, player_list: str, player_count: int,
               rounds: int, coins: int, xp: int, timeout: int) -> str:
    openers = [
        "Oh my~ ♡  Another gamble begins.",
        "Ahahaha~ ♡  My heart is already racing.",
        "How delightful~  The stage is set.",
        "Ohhh~  I can feel it already. That sweet, sweet thrill.",
        "My hands are trembling with excitement~ ♡",
    ]
    return (
        f"<blockquote>🃏 <b>REACTION BATTLE</b>  ·  Best of {rounds}</blockquote>\n\n"
        f"<i>❝ {random.choice(openers)} ❞</i>\n\n"
        f"🎴 Host: <b>{host_name}</b>\n\n"
        f"<b>The Rules of this Madness:</b>\n"
        f"  ◈ Wait for the <b>⚡ TAP NOW!</b> button\n"
        f"  ◈ Slam it faster than everyone else\n"
        f"  ◈ 😈 Fake signals will try to break your mind\n"
        f"  ◈ Win <b>2 of {rounds} rounds</b> — then you own this game\n\n"
        f"💰 <b>{coins} coins  ·  ✨ {xp} XP</b> await the winner\n\n"
        f"👥 <b>Players ({player_count}):</b>\n"
        f"{player_list}\n\n"
        f"⏳ <i>Auto-starts in {timeout}s... or let the host pull the trigger.</i>"
    )


def lobby_updated_text(host_name: str, player_list: str, player_count: int, rounds: int) -> str:
    joins = [
        "Oh? Another soul drawn into the madness~ ♡",
        "More players~  The excitement just doubled.",
        "Ahahaha~  The table grows crowded. Wonderful.",
        "Every new player makes my heart race faster~ ♡",
    ]
    return (
        f"<blockquote>🃏 <b>REACTION BATTLE</b>  ·  Best of {rounds}</blockquote>\n\n"
        f"<i>❝ {random.choice(joins)} ❞</i>\n\n"
        f"🎴 Host: <b>{host_name}</b>\n\n"
        f"👥 <b>Players ({player_count}):</b>\n"
        f"{player_list}\n\n"
        f"<i>Waiting for the host to start... or for courage to arrive.</i>"
    )


# ── Not Enough Players ────────────────────────────────────────────────────────

def not_enough_players_text(needed: int) -> str:
    return (
        f"<blockquote>😔 <b>Game Cancelled</b></blockquote>\n\n"
        f"<i>❝ How disappointing~  No one came to play with me. ❞</i>\n\n"
        f"Not enough brave souls joined.\n"
        f"I need at least <b>{needed} players</b> to feel the thrill.\n\n"
        f"<i>Come back when you've found your courage.</i>"
    )


# ── Series Start ──────────────────────────────────────────────────────────────

def series_start_text(player_list: str, player_count: int, rounds: int) -> str:
    intros = [
        "Now then~  Shall we begin this beautiful madness?",
        "Ahahaha~  The moment I've been waiting for! ♡",
        "Oh, I'm so excited I can barely breathe~ ♡",
        "Let the game begin~  May the fastest mind win.",
        "This is it~  The moment where everything is on the line!",
    ]
    return (
        f"<blockquote>🚀 <b>THE BATTLE BEGINS!</b></blockquote>\n\n"
        f"<i>❝ {random.choice(intros)} ❞</i>\n\n"
        f"👥 <b>{player_count} players locked in:</b>\n"
        f"{player_list}\n\n"
        f"🎯 Format: <b>Best of {rounds} Rounds</b>\n"
        f"😈 <b>Fake-outs are active.</b>  Trust nothing.\n\n"
        f"<i>Steady your nerves...  3...  2...  1...</i>"
    )


# ── Round Intro ───────────────────────────────────────────────────────────────

def round_intro_text(round_num: int, total_rounds: int, player_count: int) -> str:
    taunts = [
        "The button will come when it pleases~  Not a moment sooner.",
        "I wonder~  Which of you will crack first?",
        "Your fingers are trembling, aren't they~? ♡",
        "Don't blink.  Don't breathe.  Just feel.",
        "Ahahaha~  The anticipation is almost unbearable, isn't it?",
        "Every millisecond matters here.  Every. Single. One.",
        "Calm your heart~  Or let it race.  Both work against you.",
    ]
    return (
        f"<blockquote>⚡ <b>Round {round_num}  /  {total_rounds}</b></blockquote>\n\n"
        f"<i>❝ {random.choice(taunts)} ❞</i>\n\n"
        f"👀  <b>{player_count} competitors</b> — fingers ready.\n\n"
        f"<i>⚠️  Fake signals incoming.  Stay sharp.</i>"
    )


# ── Fake-out ──────────────────────────────────────────────────────────────────

def fake_out_text() -> str:
    taunts = [
        "Ahahaha~  Did your heart skip?  ♡  Don't tap that~",
        "Oh~?  Were you about to tap?  How adorable.",
        "That button~  is a lie~  ♡  Just like trust.",
        "Shh~  Not yet.  That one is mine to laugh at.",
        "How delightful~  I can practically hear your panic.",
        "Your instincts betrayed you~  The real one is still coming.",
    ]
    return (
        f"<blockquote>😈 <b>F A K E</b></blockquote>\n\n"
        f"<i>❝ {random.choice(taunts)} ❞</i>\n\n"
        f"<b>DON'T TAP THAT.</b>  It's a decoy.\n"
        f"<i>The real button is still waiting for you...</i>"
    )


def fake_out_gone_text() -> str:
    taunts = [
        "Gone~  Now stay focused.  The real one comes next.",
        "Ahahaha~  You survived the fake.  The real test begins.",
        "Good~  You didn't fall for it.  Yet.",
        "The fake is gone~  Breathe.  Then get ready.",
    ]
    return (
        f"<blockquote>👁️ <b>Fake Gone</b></blockquote>\n\n"
        f"<i>❝ {random.choice(taunts)} ❞</i>\n\n"
        f"<i>The real button is coming...  very soon.</i>"
    )


# ── TAP NOW! ──────────────────────────────────────────────────────────────────

def tap_now_text(round_num: int) -> str:
    screams = [
        "NOW! NOW! NOW!",
        "THIS IS IT!",
        "DON'T HESITATE!",
        "YOUR MOMENT!",
        "MOVE! MOVE! MOVE!",
    ]
    return (
        f"<blockquote>⚡ <b>{random.choice(screams)}</b></blockquote>\n\n"
        f"<i>❝ Ahahaha~  TAP IT!  TAP IT RIGHT NOW! ♡ ❞</i>\n\n"
        f"🏆  Round <b>{round_num}</b>  —  <b>FASTEST WINS!</b>"
    )


# ── Tap Acknowledgements (popup answers) ─────────────────────────────────────

TAP_ACK_FIRST = [
    "⚡ FIRST!  You absolute beast.",
    "⚡ First tap!  Your reflexes are magnificent~",
    "⚡ You got it!  Blazing fast~  ♡",
    "⚡ FIRST!  Ahahaha~  Incredible!",
]

TAP_ACK_LATE = [
    "✅ Registered~  But someone was faster.",
    "✅ Got it~  Speed matters here, remember.",
    "✅ Tapped~  Not first, but you tried~",
    "✅ Noted~  The fastest finger already claimed it.",
]

TAP_ALREADY_DONE = [
    "⌛ Too slow~  Round already decided.",
    "⌛ The winner was already chosen~  Try next round.",
    "⌛ A moment too late~  Such is fate.",
    "⌛ This round is done~  Sharpen up for the next.",
]

FAKE_TAP_TAUNTS = [
    "😂 Ahahaha~  That was a FAKE!  How delightfully foolish~  ♡",
    "🪤 You fell right into my trap~  No point for you.",
    "🤡 A decoy~  and you tapped it like your life depended on it~",
    "👀 Oh~?  Too eager~  That button was never real.",
    "😈 Gotcha~  ♡  The real one is still waiting for you.",
    "💀 Betrayed by your own instincts~  Magnificent.",
]

NOT_IN_GAME_TAUNT = [
    "🚫 You're not in this game~  Watch from the sidelines like a good spectator.",
    "🚫 This game isn't yours~  Join next time.",
    "🚫 Uninvited fingers~  How rude~",
]


def tap_ack(position: int, ms: int, tier_str: str) -> str:
    if position == 1:
        base = random.choice(TAP_ACK_FIRST)
    else:
        base = random.choice(TAP_ACK_LATE)
    return f"{base}  ⏱️ {ms}ms  {tier_str}"


def tap_too_late() -> str:
    return random.choice(TAP_ALREADY_DONE)


def fake_tap_taunt() -> str:
    return random.choice(FAKE_TAP_TAUNTS)


def not_in_game() -> str:
    return random.choice(NOT_IN_GAME_TAUNT)


# ── Round Timeout ─────────────────────────────────────────────────────────────

def round_timeout_text(round_num: int) -> str:
    shames = [
        "Not a single soul tapped in time~  How utterly disappointing.",
        "The button appeared and vanished~  No one brave enough.",
        "Ahahaha~  Everyone froze?  How deliciously cowardly~",
        "Nobody moved~  Did fear finally win over you?",
    ]
    return (
        f"<blockquote>⌛ <b>Round {round_num} — Timeout</b></blockquote>\n\n"
        f"<i>❝ {random.choice(shames)} ❞</i>\n\n"
        f"No point awarded this round~\n"
        f"<i>Compose yourselves for the next.</i>"
    )


# ── Round Result ──────────────────────────────────────────────────────────────

def round_result_text(
    round_num: int,
    winner_name: str,
    winner_ms: int,
    tier_str: str,
    result_lines: str,
    scoreboard: str,
) -> str:
    praises = [
        f"<b>{winner_name}</b> was the fastest~  ♡  Magnificent.",
        f"Ahahaha~  <b>{winner_name}</b> claimed it!  Such speed~",
        f"<b>{winner_name}</b>~  Your reflexes are a work of art.",
        f"Oh my~  <b>{winner_name}</b> didn't even hesitate~  ♡",
        f"<b>{winner_name}</b> wins this round~  I'm genuinely impressed.",
    ]
    return (
        f"<blockquote>🏁 <b>Round {round_num} — Result</b></blockquote>\n\n"
        f"<i>❝ {random.choice(praises)} ❞</i>\n\n"
        f"⚡ Winner: <b>{winner_name}</b>  {tier_str}\n"
        f"⏱️ Time:   <code>{winner_ms}ms</code>\n\n"
        f"📊 <b>All Taps This Round:</b>\n{result_lines}\n\n"
        f"📈 <b>Series Scoreboard:</b>\n{scoreboard}"
    )


# ── Series Clinch (mid-series someone hits wins_needed) ──────────────────────

def series_clinch_text(winner_name: str, wins: int, rounds: int) -> str:
    return (
        f"<blockquote>🔥 <b>Series Clinched!</b></blockquote>\n\n"
        f"<i>❝ Ahahaha~  <b>{winner_name}</b> has claimed victory~  ♡ ❞</i>\n\n"
        f"🏆 <b>{winner_name}</b> wins <b>{wins}/{rounds}</b> rounds — unstoppable!"
    )


# ── Final Victory ─────────────────────────────────────────────────────────────

def victory_text(
    champion_name: str,
    champ_wins: int,
    total_rounds: int,
    is_perfect: bool,
    round_log: str,
    loser_text: str,
    coins: int,
    xp: int,
    loser_xp: int,
    streak_info: str = "",
    level_up_info: str = "",
) -> str:
    closers = [
        "What a rush~  My entire body is tingling~  ♡",
        "Ahahaha~  That was absolutely beautiful.  Every second of it.",
        "A true gambler's thrill~  I haven't felt this alive in ages~  ♡",
        "The fastest mind wins~  And tonight, that was <b>you</b>.",
        "Oh~  I do love a good battle~  ♡  More~  I want more~",
    ]
    perfect_badge = "💎 <b>PERFECT SERIES — UNDEFEATED!</b>\n\n" if is_perfect else ""

    return (
        f"<blockquote>🏆 <b>REACTION BATTLE — OVER</b></blockquote>\n\n"
        f"{perfect_badge}"
        f"<i>❝ {random.choice(closers)} ❞</i>\n\n"
        f"👑 Champion: <b>{champion_name}</b>\n"
        f"🎯 Rounds Won: <b>{champ_wins} / {total_rounds}</b>\n\n"
        f"📜 <b>Round Log:</b>\n{round_log}\n\n"
        f"💰 +<b>{coins}</b> coins  ·  ✨ +<b>{xp}</b> XP\n"
        f"{streak_info}"
        f"{level_up_info}"
        f"📉 Runners-up: {loser_text}  (+{loser_xp} XP for daring to play~)"
    )


def no_winner_text() -> str:
    return (
        f"<blockquote>😴 <b>No Winner</b></blockquote>\n\n"
        f"<i>❝ Not a single soul claimed victory~  How tragically empty. ❞</i>\n\n"
        f"The series ended with no taps recorded.\n"
        f"<i>Come back when you're ready to actually gamble.</i>"
    )


# ── Streak Info ───────────────────────────────────────────────────────────────

def streak_bonus_text(streak: int, bonus: int) -> str:
    if streak >= 10:
        return f"🔥 <b>{streak}-game win streak!  +{bonus} bonus coins~  ♡  LEGENDARY!</b>\n"
    if streak >= 5:
        return f"🔥 <b>{streak}-game win streak!  +{bonus} bonus coins~  On fire!</b>\n"
    if streak >= 3:
        return f"🔥 <b>{streak}-game win streak!  +{bonus} bonus coins~</b>\n"
    return ""


# ── Level Up ──────────────────────────────────────────────────────────────────

def level_up_text(level: int, rank_title: str) -> str:
    msgs = [
        f"⬆️ <b>LEVEL UP!</b>  You've reached <b>Level {level}</b>~  {rank_title}  ♡\n",
        f"⬆️ <b>Level {level} unlocked!</b>  You're becoming something dangerous~  {rank_title}\n",
        f"⬆️ <b>Rank achieved:</b>  {rank_title}  ·  Level {level}  ·  Magnificent~  ♡\n",
    ]
    return random.choice(msgs)


# ── Stats Messages ────────────────────────────────────────────────────────────

def stats_text(
    name: str,
    global_rank: int,
    rank_title: str,
    level: int,
    xp: int,
    coins: int,
    games_played: int,
    games_won: int,
    games_lost: int,
    win_streak: int,
    best_streak: int,
    r_played: int,
    r_won: int,
    best_ms,
    avg_ms,
    fake_dodged: int,
    perfect_series: int,
) -> str:
    best_str = f"<code>{best_ms}ms</code>" if best_ms else "—"
    avg_str  = f"<code>{avg_ms}ms</code>"  if avg_ms  else "—"

    flavor = [
        "Every number tells a story of risk and reward~  ♡",
        "Your stats are your soul~  laid bare on the table.",
        "This is who you are when the button appears~",
        "Numbers don't lie~  Unlike certain fake-out buttons~  ♡",
    ]

    return (
        f"<blockquote>🎴 <b>Your Battle Record</b></blockquote>\n\n"
        f"<i>❝ {random.choice(flavor)} ❞</i>\n\n"
        f"👤 <b>{name}</b>\n"
        f"🏅 Global Rank: <b>#{global_rank}</b>  ·  {rank_title}\n"
        f"📈 Level: <b>{level}</b>  ·  ✨ XP: <b>{xp}</b>\n"
        f"💰 Coins: <b>{coins}</b>\n\n"
        f"<b>General:</b>\n"
        f"  🎮 Played:  <b>{games_played}</b>\n"
        f"  🏆 Won:     <b>{games_won}</b>\n"
        f"  💀 Lost:    <b>{games_lost}</b>\n\n"
        f"<b>Reaction Battle:</b>\n"
        f"  ⚡ Played:       <b>{r_played}</b>\n"
        f"  🥇 Won:         <b>{r_won}</b>\n"
        f"  ⏱️ Best Time:   {best_str}\n"
        f"  📊 Avg Time:    {avg_str}\n\n"
        f"<b>Streaks & Mastery:</b>\n"
        f"  🔥 Win Streak:       <b>{win_streak}</b>\n"
        f"  🏅 Best Streak:      <b>{best_streak}</b>\n"
        f"  😈 Fake-outs Dodged: <b>{fake_dodged}</b>\n"
        f"  💎 Perfect Series:   <b>{perfect_series}</b>"
    )


# ── Leaderboard ───────────────────────────────────────────────────────────────

def leaderboard_header(title: str) -> str:
    flavors = [
        "The strong rise~  The weak watch from below~  ♡",
        "Every name here earned their place through thrill and risk~",
        "Ahahaha~  Look at these magnificent gamblers~  ♡",
        "The table of legends~  How exciting~",
    ]
    return (
        f"<blockquote>📊 <b>{title}</b></blockquote>\n\n"
        f"<i>❝ {random.choice(flavors)} ❞</i>\n\n"
    )


def leaderboard_footer() -> str:
    return (
        f"\n\n<i>Use /leaderboard wins  ·  /leaderboard reaction\n"
        f"to see other rankings~  ♡</i>"
    )


# ── Error / Edge Cases ────────────────────────────────────────────────────────

ALREADY_RUNNING = (
    "⚠️ <b>A game is already running~</b>\n\n"
    "<i>❝ How greedy~  One battle at a time, darling. ❞</i>\n\n"
    "Tap <b>Join Game</b> to enter the current battle."
)

NO_GAME_FOUND = (
    "<i>❝ There's no game here~  Did you imagine it? ❞</i>"
)

HOST_ONLY_START = (
    "🚫 <i>Only the host can start~  Patience is a virtue~  ♡</i>"
)

HOST_ONLY_CANCEL = (
    "🚫 <i>Only the host can cancel~  It's their game to end.</i>"
)

ALREADY_STARTED_JOIN = (
    "⚡ <i>The battle already began~  You're too late~  ♡</i>"
)

ALREADY_JOINED = (
    "✅ <i>You're already in~  Relax and sharpen your fingers~  ♡</i>"
)

GAME_FULL = (
    "🚫 <i>The table is full~  20 players maximum.  Watch and learn~</i>"
)

NO_STATS_YET = (
    "❌ <b>No record found~</b>\n\n"
    "<i>❝ You haven't played yet~  The table awaits you.  Use /reaction ❞</i>"
)

NO_LEADERBOARD_DATA = (
    "📭 <b>Empty~</b>\n\n"
    "<i>❝ No data yet~  Someone needs to start playing.  ❞</i>"
)

CANCELLED_TEXT = (
    "<blockquote>❌ <b>Game Cancelled</b></blockquote>\n\n"
    "<i>❝ How unfortunate~  The host lost their nerve.  ❞</i>\n\n"
    "The Reaction Battle has been called off."
)