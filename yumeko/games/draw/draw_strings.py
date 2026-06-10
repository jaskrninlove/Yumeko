# ==========================================================
#  Yumeko Games Bot — Yumeko Sketch Strings
#  Copyright (c) 2026 Jass
# ==========================================================

from yumeko.games.draw.draw_game import (
    JOIN_TIME, DRAW_TIME, GUESS_TIME, ROUNDS,
    MIN_PLAYERS, MAX_PLAYERS,
    WIN_COINS, WIN_XP, LOSE_XP,
    POINTS_FAST, POINTS_MID, POINTS_SLOW, POINTS_DRAWER, POINTS_BONUS,
    masked_word, format_scoreboard, format_players_list,
)


def lobby_text(game: dict) -> str:
    count = len(game["players"])
    return (
        "<blockquote>🎨 <b>Yumeko Sketch</b></blockquote>\n\n"
        "<i>❝ Ahahaha~ can you draw what your heart is hiding?\n"
        "Or will your scribbles betray you first? ♡ ❞</i>\n\n"
        f"🖌 <b>Host:</b> {game['host_name']}\n"
        f"👥 <b>Players:</b> <code>{count}/{MAX_PLAYERS}</code>\n"
        f"🔄 <b>Rounds:</b> <code>{ROUNDS}</code>\n"
        f"⏳ <b>Join Timer:</b> <code>{JOIN_TIME}s</code>\n\n"
        "━━━━━━━━━━━━━━\n"
        "🪑 <b>Seated Players</b>\n\n"
        f"{format_players_list(game)}\n"
        "━━━━━━━━━━━━━━\n\n"
        f"🏆 Fast guess: <b>+{POINTS_FAST}</b> · Normal: <b>+{POINTS_MID}</b> · Late: <b>+{POINTS_SLOW}</b>\n"
        f"🖌 Artist earns <b>+{POINTS_DRAWER}</b> per correct guesser\n\n"
        "🎲 <i>Tap below to join before the canvas opens.</i>"
    )


def not_enough_text(game: dict) -> str:
    return (
        "<blockquote>😔 <b>Yumeko Sketch Cancelled</b></blockquote>\n\n"
        f"Only <b>{len(game['players'])}</b> player(s) joined.\n"
        f"Need at least <b>{MIN_PLAYERS}</b> to play.\n\n"
        "<i>Start again when more artists are ready.</i>"
    )


def join_countdown_text(seconds: int) -> str:
    return (
        f"<blockquote>⏳ <b>Lobby closes in {seconds}s</b></blockquote>\n\n"
        f"<i>❝ Last chance to sit at the canvas table. ♡ ❞</i>"
    )


def game_starting_text(game: dict) -> str:
    order = game["order"]
    turn_list = "\n".join(
        f"  {i+1}. <a href=\"tg://user?id={uid}\">{game['players'][uid]['name']}</a>"
        for i, uid in enumerate(order)
    )
    return (
        "<blockquote>🎨 <b>Yumeko Sketch — Starting!</b></blockquote>\n\n"
        f"<i>❝ {ROUNDS} rounds. Every soul draws. Every soul guesses. ♡ ❞</i>\n\n"
        f"📋 <b>Turn Order</b>\n{turn_list}\n\n"
        f"🕐 Draw time: <b>{DRAW_TIME}s</b> per turn\n\n"
        "<i>First artist is being picked…</i>"
    )


def round_banner_text(game: dict) -> str:
    return (
        f"<blockquote>🔄 <b>Round {game['round']} of {ROUNDS}</b></blockquote>\n\n"
        f"<b>Scoreboard</b>\n{format_scoreboard(game)}"
    )


def drawer_pick_dm(choices: list[str], name: str) -> str:
    lines = "\n".join(f"  {i+1}. <code>{w}</code>" for i, w in enumerate(choices))
    return (
        "<blockquote>🎨 <b>It's Your Turn to Draw!</b></blockquote>\n\n"
        f"<i>❝ The canvas is yours, {name}.\n"
        f"Choose your word and make them guess it. ♡ ❞</i>\n\n"
        f"Pick one word:\n\n{lines}\n\n"
        "⏳ You have <b>30 seconds</b> to choose or a word is auto-selected."
    )


def drawing_phase_group_text(g: dict) -> str:
    drawer_id = g["current_drawer"]
    drawer = g["players"].get(drawer_id, {})
    drawer_name = drawer.get("name", "Someone")

    word = g.get("current_word")
    masked = masked_word(word) if word else "_ " * 3

    return (
        "<blockquote>🖌️ <b>Drawing Phase</b></blockquote>\n\n"
        "<i>❝ The artist has received the secret word. "
        "The canvas is waiting in their inbox. ♡ ❞</i>\n\n"
        f"🎨 Artist: <a href=\"tg://user?id={drawer_id}\"><b>{drawer_name}</b></a>\n"
        f"📩 Status: <b>Check your inbox and open the canvas.</b>\n"
        f"📝 Word: <code>{masked}</code> "
        f"(<b>{len(word.replace(' ', '')) if word else 0}</b> letters)\n\n"
        f"⏳ Drawing time: <b>{DRAW_TIME}s</b>\n\n"
        "<i>The drawing will appear here after submission.\n"
        "Guessing will start when the artwork is posted.</i>"
    )


def canvas_dm_text(word: str) -> str:
    return (
        "<blockquote>🖌 <b>Open Your Canvas</b></blockquote>\n\n"
        f"Your secret word: <tg-spoiler><b>{word.upper()}</b></tg-spoiler>\n\n"
        f"⏳ You have <b>{DRAW_TIME} seconds</b> to draw and submit.\n\n"
        "<b>Rules:</b>\n"
        "🚫 No letters or numbers in the drawing\n"
        "🚫 No symbols that spell the word\n"
        "✅ Use shapes, colors, stick figures — anything goes!\n\n"
        "<i>❝ Make them feel it before they name it. ♡ ❞</i>\n\n"
        "👇 Tap below to open the drawing canvas."
    )


def guessing_phase_text(game: dict, hint: str = "") -> str:
    drawer  = game["players"].get(game["current_drawer"], {})
    name    = drawer.get("name", "Someone")
    uid     = game["current_drawer"]
    word    = game["current_word"] or ""
    display = hint if hint else masked_word(word)
    guessed_count   = len(game.get("guessed", {}))
    total_guessers  = len(game["players"]) - 1

    # Build guessed list
    guessed_names = []
    for gid in game.get("guessed", {}):
        p = game["players"].get(gid)
        if p:
            guessed_names.append(f"✅ {p['name']}")

    guessed_section = ""
    if guessed_names:
        guessed_section = "\n" + "\n".join(guessed_names) + "\n"

    return (
        "<blockquote>🤔 <b>Guess the Drawing!</b></blockquote>\n\n"
        "<i>❝ What is this soul trying to tell you? ♡ ❞</i>\n\n"
        f"🖌 <b>Artist:</b> <a href=\"tg://user?id={uid}\">{name}</a>\n"
        f"📝 <b>Word:</b> <code>{display}</code>  ({len(word.replace(' ',''))} letters)\n"
        f"👥 <b>Guessed:</b> {guessed_count}/{total_guessers}"
        f"{guessed_section}\n"
        f"⏳ Remaining: <b>{DRAW_TIME}s</b>\n\n"
        "<i>Type your guess in the chat!</i>"
    )


def correct_guess_announcement(name: str, pts: int, elapsed: float, uid: int) -> str:
    if elapsed <= 20:
        tag = "⚡ <b>LIGHTNING!</b>"
    elif elapsed <= 50:
        tag = "✨ <b>Quick!</b>"
    else:
        tag = "🐢 <i>Better late than never~</i>"
    return (
        f"✅ <a href=\"tg://user?id={uid}\">{name}</a> guessed it! "
        f"+<b>{pts}</b> pts  {tag}"
    )


def close_guess_announcement(name: str, guess: str) -> str:
    return f"🔥 <b>{name}:</b> <i>\"{guess}\"</i> — so close, darling~"


def hint_announcement(hint_str: str, level: int) -> str:
    msgs = [
        "One letter revealed. Getting warmer~",
        "Two letters revealed. Think carefully.",
        "Almost there. The answer is right in front of you.",
    ]
    msg = msgs[min(level-1, 2)]
    return (
        f"💡 <b>Hint {level}:</b> <code>{hint_str}</code>\n"
        f"<i>{msg}</i>"
    )


def turn_end_text(game: dict, word: str, everyone_got_it: bool, drawer_uid: int) -> str:
    guessed_count  = len(game.get("guessed", {}))
    total_guessers = len(game["players"]) - 1

    if everyone_got_it:
        headline = "🎉 <b>Everyone guessed it!</b> Magnificent drawing, darling."
    elif guessed_count == 0:
        headline = "😔 <b>Nobody guessed it.</b> The drawing was… <i>abstract</i>."
    else:
        headline = f"⏰ <b>Time's up!</b> {guessed_count}/{total_guessers} players guessed."

    drawer = game["players"].get(drawer_uid, {})
    drawer_name = drawer.get("name", "The artist")

    return (
        "<blockquote>⏰ <b>Turn Over</b></blockquote>\n\n"
        f"{headline}\n\n"
        f"🔑 The word was: <b>{word.upper()}</b>\n"
        f"🖌 <b>{drawer_name}</b> was the artist.\n\n"
        f"<b>Scores</b>\n{format_scoreboard(game)}"
    )


def no_dm_text(name: str) -> str:
    return (
        f"⚠️ <b>{name}</b> needs to start the bot in DM first!\n"
        "A word has been auto-assigned."
    )


def winner_text(game: dict) -> str:
    winner = max(game["players"].values(), key=lambda p: p["score"], default=None)
    if not winner:
        return "<blockquote>🎨 <b>Game Over</b></blockquote>\n\nNo winner."

    uid    = winner["id"]
    board  = format_scoreboard(game)

    return (
        "<blockquote>🏆 <b>Yumeko Sketch — Game Over!</b></blockquote>\n\n"
        "<i>❝ The canvas is empty. The table has decided. ♡ ❞</i>\n\n"
        f"🎨 <b>Champion:</b> "
        f"<a href=\"tg://user?id={uid}\">{winner['name']}</a> "
        f"with <b>{winner['score']}</b> points\n\n"
        f"🏆 Winner: +<b>{WIN_COINS}</b> coins | +<b>{WIN_XP}</b> XP\n"
        f"📉 Others: +<b>{LOSE_XP}</b> XP\n\n"
        f"<b>Final Scoreboard</b>\n{board}"
    )