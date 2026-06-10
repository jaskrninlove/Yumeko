# ==========================================================
#  Yumeko Games Bot — Yumeko Sketch Handler
#  Copyright (c) 2026 Jass
# ==========================================================

import asyncio
import base64
import io
import json
import urllib.parse

from pyrogram import filters
from pyrogram.enums import ChatType, ParseMode
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    WebAppInfo,
)

from yumeko.core.game_manager import is_game_running, get_running_game, lock_game, unlock_game
from yumeko.core.logger import game_started, game_finished
from yumeko.database.users import add_user, add_win, add_loss
from yumeko.helpers.permissions import is_admin, is_bot_admin
from yumeko.config import config

from yumeko.games.draw.draw_game import (
    active_draw_games,
    JOIN_TIME, DRAW_TIME, ROUNDS, MIN_PLAYERS,
    POINTS_BONUS,

    create_draw_game, get_draw_game, end_draw_game, set_lobby_msg,
    join_draw_game, start_game, get_player,
    pick_word, submit_drawing, process_guess,
    all_guessed, advance_turn, get_winner, get_scoreboard,
    reveal_hint, masked_word, format_scoreboard,
    WIN_COINS, WIN_XP, LOSE_XP,
)

from yumeko.games.draw.draw_strings import (
    lobby_text, not_enough_text, join_countdown_text,
    game_starting_text, round_banner_text,
    drawer_pick_dm, drawing_phase_group_text, canvas_dm_text,
    guessing_phase_text,
    correct_guess_announcement, close_guess_announcement,
    hint_announcement, turn_end_text, winner_text, no_dm_text,
)
import io
from PIL import Image

# ──────────────────────────────────────────────
#  Config key — set DRAW_WEBAPP_URL in config.py
#  e.g. config.DRAW_WEBAPP_URL = "https://yumeko-sketch.vercel.app"
# ──────────────────────────────────────────────
def _webapp_url(word: str, chat_id: int, msg_id: int | None = None) -> str:
    base = getattr(config, "DRAW_WEBAPP_URL", "https://yumeko-canvas.vercel.app/").rstrip("/")
    params = urllib.parse.urlencode(
        {
            "word": word,
            "chat": str(chat_id),
            "time": str(DRAW_TIME),
            "mode": "draw",
            "msg": str(msg_id or 0),
            "live": "1",
        }
    )
    return f"{base}/?{params}"

# ──────────────────────────────────────────────
#  Keyboard builders
# ──────────────────────────────────────────────

def _join_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🎨  Join Game", callback_data="sketch_join"),
    ]])

def make_blank_canvas():
    img = Image.new("RGB", (900, 650), "white")
    bio = io.BytesIO()
    img.save(bio, "JPEG", quality=90)
    bio.name = "yumeko_canvas.jpg"
    bio.seek(0)
    return bio

def _word_pick_kb(choices: list[str]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"✦  {w.capitalize()}", callback_data=f"sketch_word_{w}")]
        for w in choices
    ])


def _canvas_kb(word: str, chat_id: int, msg_id: int | None = None) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(
            "🖌️ Open Canvas",
            web_app=WebAppInfo(url=_webapp_url(word, chat_id, msg_id)),
        )
    ]])

def _hints_kb(chat_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("💡  Hint", callback_data=f"sketch_hint_{chat_id}"),
    ]])


def _want_to_draw_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✋  I Want to Draw!", callback_data="sketch_want_draw"),
    ]])


# ──────────────────────────────────────────────
#  Helpers
# ──────────────────────────────────────────────

def _find_user_game(user_id: int):
    for cid, g in active_draw_games.items():
        if user_id in g["players"]:
            return cid
    return None


async def _update_lobby(client, chat_id: int):
    g = get_draw_game(chat_id)
    if not g or not g.get("lobby_msg_id"):
        return
    try:
        await client.edit_message_text(
            chat_id=chat_id,
            message_id=g["lobby_msg_id"],
            text=lobby_text(g),
            parse_mode=ParseMode.HTML,
            reply_markup=_join_kb(),
            disable_web_page_preview=True,
        )
    except Exception:
        pass


async def _update_guess_msg(client, chat_id: int, hint: str = ""):
    """Edit the pinned guessing message with updated guesser list."""
    g = get_draw_game(chat_id)
    if not g or not g.get("group_msg_id"):
        return
    try:
        await client.edit_message_caption(
            chat_id=chat_id,
            message_id=g["group_msg_id"],
            caption=guessing_phase_text(g, hint),
            parse_mode=ParseMode.HTML,
            reply_markup=_hints_kb(chat_id),
        )
    except Exception:
        pass


# ──────────────────────────────────────────────
#  Command: /sketch  /draw  /skribbl
# ──────────────────────────────────────────────

async def sketch_cmd(client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        await message.reply_text("Yumeko Sketch can only be played in groups~")
        return

    chat_id = message.chat.id
    user    = message.from_user
    if not user:
        return

    if not await is_admin(client, chat_id, user.id):
        await message.reply_text("Only admins can start Yumeko Sketch.")
        return

    if not await is_bot_admin(client, chat_id):
        await message.reply_text("Please make me an admin first, darling~")
        return

    if is_game_running(chat_id):
        await message.reply_text(
            f"<b>{get_running_game(chat_id)}</b> is already running!",
            parse_mode=ParseMode.HTML,
        )
        return

    await add_user(user)
    game = create_draw_game(chat_id, user.id, user.first_name or "Unknown")
    lock_game(chat_id, "Yumeko Sketch")
    join_draw_game(chat_id, user)
    game_started("Yumeko Sketch", chat_id)

    # Send lobby with GIF
    try:
        sent = await client.send_animation(
            chat_id,
            getattr(config, "DRAW_START_GIF", "https://media.giphy.com/media/drawing/giphy.gif"),
            caption=lobby_text(game),
            parse_mode=ParseMode.HTML,
            reply_markup=_join_kb(),
        )
    except Exception:
        sent = await message.reply_text(
            lobby_text(game),
            parse_mode=ParseMode.HTML,
            reply_markup=_join_kb(),
            disable_web_page_preview=True,
        )

    set_lobby_msg(chat_id, sent.id)
    asyncio.create_task(_join_countdown(client, chat_id))


# ──────────────────────────────────────────────
#  Join Countdown
# ──────────────────────────────────────────────

async def _join_countdown(client, chat_id: int):
    # Warn at 15s remaining
    await asyncio.sleep(max(JOIN_TIME - 15, 1))

    g = get_draw_game(chat_id)
    if not g or g["status"] != "joining":
        return

    await client.send_message(
        chat_id, join_countdown_text(15), parse_mode=ParseMode.HTML,
    )
    await asyncio.sleep(15)

    g = get_draw_game(chat_id)
    if not g or g["status"] != "joining":
        return

    if len(g["players"]) < MIN_PLAYERS:
        await client.send_message(chat_id, not_enough_text(g), parse_mode=ParseMode.HTML)
        end_draw_game(chat_id)
        unlock_game(chat_id)
        return

    g = start_game(chat_id)

    # Announce start + turn order
    try:
        await client.send_animation(
            chat_id,
            getattr(config, "DRAW_ROUND_GIF", ""),
            caption=game_starting_text(g),
            parse_mode=ParseMode.HTML,
        )
    except Exception:
        await client.send_message(
            chat_id, game_starting_text(g), parse_mode=ParseMode.HTML,
        )

    await asyncio.sleep(3)
    await _begin_turn(client, chat_id)


# ──────────────────────────────────────────────
#  Turn Flow
# ──────────────────────────────────────────────
async def sketch_end_cmd(client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        return

    chat_id = message.chat.id
    user = message.from_user

    if not user:
        return

    g = get_draw_game(chat_id)

    if not g:
        await message.reply_text("No Sketch game is running right now.")
        return

    if not await is_admin(client, chat_id, user.id):
        await message.reply_text("Only admins can end the Sketch game.")
        return

    try:
        if g.get("drawing_msg_id"):
            await client.unpin_chat_message(chat_id, g["drawing_msg_id"])
    except Exception:
        pass

    end_draw_game(chat_id)
    unlock_game(chat_id)

    await message.reply_text(
        "<blockquote>🛑 <b>Sketch Game Ended</b></blockquote>\n\n"
        "<i>❝ The canvas has closed. The table is silent again. ♡ ❞</i>",
        parse_mode=ParseMode.HTML,
    )

async def _begin_turn(client, chat_id: int):
    g = get_draw_game(chat_id)
    if not g:
        return

    drawer_id = g["current_drawer"]
    drawer = g["players"].get(drawer_id, {})
    drawer_name = drawer.get("name", "Someone")

    # 1) FIRST announce in group whose turn it is
    await client.send_message(
        chat_id,
        (
            "<blockquote>🎨 <b>Artist Turn</b></blockquote>\n\n"
            f"🖌 Artist: <a href=\"tg://user?id={drawer_id}\"><b>{drawer_name}</b></a>\n\n"
            "<i>❝ Yumeko has chosen the next hand.\n"
            "Check your inbox, pick a word, and open the canvas. ♡ ❞</i>\n\n"
            "📩 <b>Word choices are being sent to the artist now.</b>"
        ),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

    # 2) Small delay so group message appears first
    await asyncio.sleep(1)

    # 3) THEN send DM word choices
    try:
        await client.send_message(
            drawer_id,
            drawer_pick_dm(g["word_choices"], drawer_name),
            parse_mode=ParseMode.HTML,
            reply_markup=_word_pick_kb(g["word_choices"]),
        )

    except Exception:
        await client.send_message(
            chat_id,
            no_dm_text(drawer_name),
            parse_mode=ParseMode.HTML,
        )

        # Auto-pick first word if DM fails
        pick_word(chat_id, drawer_id, g["word_choices"][0])
        await _after_word_picked(client, chat_id)
        return

    # 4) Start word-pick timer only after DM is sent
    asyncio.create_task(
        _word_pick_timeout(
            client,
            chat_id,
            drawer_id,
            g["round"],
            g["turn_index"],
        )
    )

async def _word_pick_timeout(client, chat_id: int, drawer_id: int, round_: int, turn_idx: int):
    await asyncio.sleep(30)
    g = get_draw_game(chat_id)
    if not g or g["round"]!=round_ or g["turn_index"]!=turn_idx:
        return
    if g["status"] != "word_pick" or g["current_drawer"] != drawer_id:
        return
    # Auto-pick
    word = g["word_choices"][0]
    pick_word(chat_id, drawer_id, word)
    try:
        await client.send_message(
            drawer_id,
            f"⏰ Time's up! Auto-selected: <tg-spoiler><b>{word.upper()}</b></tg-spoiler>",
            parse_mode=ParseMode.HTML,
        )
    except Exception:
        pass
    await _after_word_picked(client, chat_id)


async def _after_word_picked(client, chat_id: int):
    """Send canvas DM to drawer + start guessing timer."""
    g = get_draw_game(chat_id)
    if not g:
        return

    drawer_id = g["current_drawer"]
    word = g["current_word"]

    try:
        await client.send_message(
            drawer_id,
            canvas_dm_text(word),
            parse_mode=ParseMode.HTML,
            reply_markup=_canvas_kb(word, chat_id, g.get("live_msg_id")),
        )
    except Exception:
        pass

    sent = await client.send_photo(
        chat_id,
        make_blank_canvas(),
        caption=drawing_phase_group_text(g),
        parse_mode=ParseMode.HTML,
    )
    g["live_msg_id"] = sent.id

    # IMPORTANT:
    # Start guessing state immediately because Vercel API posts the image,
    # but WebApp sendData may not reach Pyrogram reliably.
    ok, reason = submit_drawing(chat_id, drawer_id)

    if not ok and reason != "wrong_phase":
        print(f"[DRAW STATUS ERROR] {reason}")

    g = get_draw_game(chat_id)

    # asyncio.create_task(
    #     _guess_hint_timer(client, chat_id, g["round"], g["turn_index"])
    # )

async def _draw_timeout(client, chat_id: int, drawer_id: int, round_: int, turn_idx: int):
    """Auto-end turn if drawer never submits."""
    await asyncio.sleep(DRAW_TIME + 5)  # +5s grace
    g = get_draw_game(chat_id)
    if not g or g["round"]!=round_ or g["turn_index"]!=turn_idx:
        return
    if g["status"] != "drawing":
        return
    word = g.get("current_word","???")
    await client.send_message(
        chat_id,
        (
            "<blockquote>⏰ <b>Drawing Time Expired</b></blockquote>\n\n"
            "<i>❝ The canvas stayed empty. How mysterious. ♡ ❞</i>\n\n"
            f"The word was: <b>{word.upper()}</b>"
        ),
        parse_mode=ParseMode.HTML,
    )
    await _end_turn(client, chat_id)


# ──────────────────────────────────────────────
#  WebApp Submission  ← THE CORE FLOW
# ──────────────────────────────────────────────

async def webapp_data_handler(client, message: Message):
    web_app_data = getattr(message, "web_app_data", None)

    if not web_app_data:
        return

    user = message.from_user
    if not user:
        return

    try:
        payload = json.loads(web_app_data.data)
    except Exception:
        return

    if payload.get("type") != "drawing_submitted":
        return

    chat_id = int(payload.get("chat_id", 0))
    strokes = payload.get("strokes", 0)
    colors = payload.get("colors", 0)

    g = get_draw_game(chat_id)

    if not g:
        await message.reply_text("❌ No active Sketch game found.")
        return

    if g["current_drawer"] != user.id:
        await message.reply_text("It's not your turn to draw.")
        return

    ok, reason = submit_drawing(chat_id, user.id)

    if not ok:
        await message.reply_text(f"⚠️ Submission error: {reason}")
        return

    await message.reply_text(
        f"✅ <b>Drawing submitted!</b>\n"
        f"🖌 Strokes: <b>{strokes}</b> · 🎨 Colors: <b>{colors}</b>\n\n"
        "<i>Guessing is now active.</i>",
        parse_mode=ParseMode.HTML,
    )

    asyncio.create_task(_guess_hint_timer(client, chat_id, g["round"], g["turn_index"]))

# ──────────────────────────────────────────────
#  Hint Timer
# ──────────────────────────────────────────────

async def _guess_hint_timer(client, chat_id: int, round_: int, turn_idx: int):
    """
    Reveals hints at 1/3 and 2/3 of DRAW_TIME, then ends turn at full time.
    """
    h1 = DRAW_TIME // 3
    h2 = (DRAW_TIME * 2) // 3

    await asyncio.sleep(h1)
    g = get_draw_game(chat_id)
    if not g or g["round"]!=round_ or g["turn_index"]!=turn_idx or g["status"]!="guessing":
        return
    hint = reveal_hint(chat_id)
    if hint:
        await client.send_message(chat_id, hint_announcement(hint, 1), parse_mode=ParseMode.HTML)
        await _update_guess_msg(client, chat_id, hint)

    await asyncio.sleep(h2 - h1)
    g = get_draw_game(chat_id)
    if not g or g["round"]!=round_ or g["turn_index"]!=turn_idx or g["status"]!="guessing":
        return
    hint = reveal_hint(chat_id)
    if hint:
        await client.send_message(chat_id, hint_announcement(hint, 2), parse_mode=ParseMode.HTML)
        await _update_guess_msg(client, chat_id, hint)

    await asyncio.sleep(DRAW_TIME - h2)
    g = get_draw_game(chat_id)
    if not g or g["round"]!=round_ or g["turn_index"]!=turn_idx or g["status"]!="guessing":
        return

    await _end_turn(client, chat_id)


# ──────────────────────────────────────────────
#  Guessing Handler
# ──────────────────────────────────────────────

async def guess_handler(client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        return

    user = message.from_user
    if not user or not message.text:
        return

    # Ignore commands
    if message.text.startswith("/"):
        return

    chat_id = message.chat.id
    g = get_draw_game(chat_id)
    if not g or g["status"] != "guessing":
        return

    result, pts = process_guess(chat_id, user.id, message.text)

    if result == "correct":
        elapsed = g["guessed"].get(user.id, 0)

        # Delete the guess message so nobody else sees the word
        try:
            await message.delete()
        except Exception:
            pass

        # Announce correct guess
        await client.send_message(
            chat_id,
            correct_guess_announcement(user.first_name, pts, elapsed, user.id),
            parse_mode=ParseMode.HTML,
        )

        # Update guessing photo caption
        await _update_guess_msg(client, chat_id)

        if all_guessed(g):
            await _end_turn(client, chat_id)

    elif result == "close":
        # Quietly delete close guesses — they give it away
        try:
            await message.delete()
        except Exception:
            pass
        await client.send_message(
            chat_id,
            close_guess_announcement(user.first_name, message.text.strip()),
            parse_mode=ParseMode.HTML,
        )

    # "wrong", "already", "drawer", "not_active" → do nothing (let message stand)


# ──────────────────────────────────────────────
#  Turn End
# ──────────────────────────────────────────────

async def _end_turn(client, chat_id: int):
    g = get_draw_game(chat_id)
    if not g:
        return
    if g["status"] not in ("guessing", "drawing"):
        return

    word      = g.get("current_word", "???")
    everyone  = all_guessed(g)
    drawer_id = g["current_drawer"]

    # Unpin drawing
    if g.get("drawing_msg_id"):
        try:
            await client.unpin_chat_message(chat_id, g["drawing_msg_id"])
        except Exception:
            pass

    await client.send_message(
        chat_id,
        turn_end_text(g, word, everyone, drawer_id),
        parse_mode=ParseMode.HTML,
    )

    await asyncio.sleep(4)

    info = advance_turn(chat_id)
    g    = get_draw_game(chat_id)

    if info["game_over"]:
        await _finish_game(client, chat_id)
        return

    if info["new_round"]:
        try:
            await client.send_animation(
                chat_id,
                getattr(config, "DRAW_ROUND_GIF", ""),
                caption=round_banner_text(g),
                parse_mode=ParseMode.HTML,
            )
        except Exception:
            await client.send_message(
                chat_id, round_banner_text(g), parse_mode=ParseMode.HTML,
            )
        await asyncio.sleep(3)

    await _begin_turn(client, chat_id)


# ──────────────────────────────────────────────
#  Finish Game
# ──────────────────────────────────────────────

async def _finish_game(client, chat_id: int):
    g = get_draw_game(chat_id)
    if not g:
        return

    board  = get_scoreboard(g)
    winner = board[0] if board else None

    for i, p in enumerate(board):
        uid = p["id"]
        if i == 0:
            await add_win(uid, coins=WIN_COINS, xp=WIN_XP)
        else:
            await add_loss(uid, xp=LOSE_XP)

    try:
        await client.send_animation(
            chat_id,
            getattr(config, "DRAW_WIN_GIF", ""),
            caption=winner_text(g),
            parse_mode=ParseMode.HTML,
            reply_markup=_want_to_draw_kb(),
        )
    except Exception:
        await client.send_message(
            chat_id, winner_text(g), parse_mode=ParseMode.HTML,
            reply_markup=_want_to_draw_kb(),
        )

    game_finished("Yumeko Sketch", winner["name"] if winner else "nobody")
    end_draw_game(chat_id)
    unlock_game(chat_id)


# ──────────────────────────────────────────────
#  Callbacks
# ──────────────────────────────────────────────

async def sketch_join_callback(client, query: CallbackQuery):
    chat_id = query.message.chat.id
    user    = query.from_user

    g = get_draw_game(chat_id)
    if not g or g["status"] != "joining":
        await query.answer("No open Sketch lobby.", show_alert=True)
        return

    await add_user(user)
    ok, reason = join_draw_game(chat_id, user)

    if not ok:
        msgs = {
            "joined":  "You're already in the game~",
            "full":    "The canvas is full!",
            "started": "The game has already started.",
        }
        await query.answer(msgs.get(reason, "Cannot join now."), show_alert=True)
        return

    await query.answer("You joined Yumeko Sketch! 🎨")
    await _update_lobby(client, chat_id)


async def sketch_word_callback(client, query: CallbackQuery):
    """Drawer picks word from DM."""
    user    = query.from_user
    chat_id = _find_user_game(user.id)

    if not chat_id:
        await query.answer("No active game found.", show_alert=True)
        return

    g = get_draw_game(chat_id)
    if not g or g["status"] != "word_pick":
        await query.answer("Word pick phase is over.", show_alert=True)
        return

    if g["current_drawer"] != user.id:
        await query.answer("It's not your turn.", show_alert=True)
        return

    word = query.data.replace("sketch_word_", "", 1)
    ok, reason = pick_word(chat_id, user.id, word)

    if not ok:
        await query.answer(reason, show_alert=True)
        return

    # Edit DM to confirmation + canvas button
    try:
        await query.message.edit_text(
            f"<blockquote>✅ <b>Word Selected!</b></blockquote>\n\n"
            f"Your word: <tg-spoiler><b>{word.upper()}</b></tg-spoiler>\n\n"
            "<i>Opening your canvas now…</i>",
            parse_mode=ParseMode.HTML,
        )
    except Exception:
        pass

    await query.answer("Word locked in! ✦")
    await _after_word_picked(client, chat_id)


async def sketch_hint_callback(client, query: CallbackQuery):
    """Hint button on the drawing photo."""
    raw = query.data.replace("sketch_hint_", "", 1)
    try:
        chat_id = int(raw)
    except ValueError:
        await query.answer("Invalid hint.", show_alert=True)
        return

    g = get_draw_game(chat_id)
    if not g or g["status"] != "guessing":
        await query.answer("No active guessing phase.", show_alert=True)
        return

    # Don't let the drawer use hints
    if query.from_user.id == g["current_drawer"]:
        await query.answer("Artists can't use hints, darling~", show_alert=True)
        return

    hint = reveal_hint(chat_id)
    if not hint:
        await query.answer("No more hints available.", show_alert=True)
        return

    await query.answer(f"Hint: {hint}", show_alert=True)

    # Announce in chat
    await client.send_message(
        chat_id,
        hint_announcement(hint, g["hint_level"]),
        parse_mode=ParseMode.HTML,
    )
    await _update_guess_msg(client, chat_id, hint)


async def sketch_want_draw_callback(client, query: CallbackQuery):
    """'I want to draw!' button after game ends → suggest starting new game."""
    await query.answer("Start a new game with /sketch in your group!")
    await query.message.reply_text(
        "<i>❝ The canvas calls your name. Use /sketch to start a new game. ♡ ❞</i>",
        parse_mode=ParseMode.HTML,
    )


# ──────────────────────────────────────────────
#  Handler Registration
# ──────────────────────────────────────────────

def register_draw_handlers(app):
    # Commands
    app.add_handler(
        MessageHandler(
            sketch_cmd,
            filters.command(["sketch","draw","skribbl","skribble"]) & filters.group,
        ),
        group=190,
    )

    # WebApp data from drawing canvas (private message with web_app_data)
    app.add_handler(
        MessageHandler(
            webapp_data_handler,
            filters.private,
        ),
        group=179,   # before last-words handler so it runs first on private
    )

    # Join button
    app.add_handler(
        CallbackQueryHandler(sketch_join_callback, filters.regex("^sketch_join$")),
        group=190,
    )

    # Word pick (from DM)
    app.add_handler(
        CallbackQueryHandler(sketch_word_callback, filters.regex("^sketch_word_")),
        group=190,
    )

    # Hint button
    app.add_handler(
        CallbackQueryHandler(sketch_hint_callback, filters.regex("^sketch_hint_")),
        group=190,
    )

    # "I want to draw!" post-game
    app.add_handler(
        CallbackQueryHandler(sketch_want_draw_callback, filters.regex("^sketch_want_draw$")),
        group=190,
    )

    # Guessing — low group = high priority, runs before normal message handlers
    app.add_handler(
        MessageHandler(
            guess_handler,
            filters.group & filters.text & ~filters.service,
        ),
        group=-190,
    )
    app.add_handler(
    MessageHandler(
        sketch_end_cmd,
        filters.command(["endsketch", "stopsketch", "enddraw", "stopdraw"]) & filters.group,
    ),
    group=190,
)