# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
# ==========================================================

import asyncio

from pyrogram import filters
from pyrogram.enums import ChatType, ParseMode
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.types import Message, CallbackQuery

from yumeko.games.blackjack.handler import apply_vote_afk
from yumeko.core.game_manager import is_game_running, get_running_game, lock_game, unlock_game
from yumeko.core.logger import game_started, game_finished
from yumeko.database.users import add_user
from yumeko.helpers.permissions import is_admin, is_bot_admin
from yumeko.locales import get_text
from yumeko.config import config
from yumeko.games.mafia.media import mafia_send

from yumeko.games.mafia.game import (
    # constants
    JOIN_TIME, NIGHT_TIME, DISCUSSION_TIME, VOTE_TIME, MIN_PLAYERS,
    # game state
    active_mafia_games,
    create_game, get_game, end_game,
    add_afk_warning, get_non_voters, kill_player,
    join_game, assign_roles, role_name,
    get_player, get_alive_role,
    # night resolution
    resolve_night, reset_night,
    # voting
    start_voting, vote_player, resolve_votes,
    # win / reward
    check_winner, reward_game, calculate_mvp,
    # last words
    can_send_last_words, mark_last_words_used,
    # UI helpers
    join_button,
    # night actions
    mafia_vote, doctor_save, detective_check,
    bodyguard_protect, cupid_link,
    vigilante_shoot,
    witch_save, witch_kill,
    silence_player,
    arsonist_mark, arsonist_ignite,
    trickster_twist,
    # lobby
    set_lobby_message,
)

from yumeko.games.mafia.buttons import (
    mafia_kill_buttons,
    doctor_save_buttons,
    detective_buttons,
    bodyguard_buttons,
    cupid_first_pick_buttons,
    cupid_second_pick_buttons,
    voting_buttons,
    vigilante_buttons,
    witch_buttons,
    witch_kill_buttons,
    witch_save_buttons,
    silencer_buttons,
    arsonist_buttons,
    trickster_vote_button,
)

from yumeko.games.mafia.strings import (
    rules_text, lobby_text, join_countdown_text,
    joined_text, not_enough_text, role_guide,
    night_group_text, no_dm_text,
    mafia_action_dm, doctor_action_dm,
    detective_action_dm, bodyguard_action_dm, cupid_action_dm,
    villager_night_dm, action_saved_text,
    detective_result_text, cupid_second_text,
    discussion_text, voting_text,
    vote_recorded_text, vote_result_text, winner_text,
)


# ──────────────────────────────────────────────
#  Helpers
# ──────────────────────────────────────────────

def find_user_game(user_id: int):
    """Return the chat_id for whichever active game this user is in, or None."""
    for chat_id, game in active_mafia_games.items():
        if user_id in game["players"]:
            return chat_id
    return None


async def update_lobby_message(client, chat_id: int):
    game = get_game(chat_id)
    if not game or not game.get("lobby_message_id"):
        return
    try:
        await client.edit_message_text(
            chat_id=chat_id,
            message_id=game["lobby_message_id"],
            text=lobby_text(game),
            parse_mode=ParseMode.HTML,
            reply_markup=join_button(),
            disable_web_page_preview=True,
        )
    except Exception:
        pass


# ──────────────────────────────────────────────
#  Commands
# ──────────────────────────────────────────────

async def mafia_cmd(client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        await message.reply_text("Mafia can only be played in groups.")
        return

    chat_id = message.chat.id
    user = message.from_user

    if not user:
        return

    if not await is_admin(client, chat_id, user.id):
        await message.reply_text("Only group admins can start Mafia.")
        return

    if not await is_bot_admin(client, chat_id):
        await message.reply_text("Please make me admin first, darling.")
        return

    if is_game_running(chat_id):
        await message.reply_text(
            get_text("game_already_running_global", game=get_running_game(chat_id)),
            parse_mode=ParseMode.HTML,
        )
        return

    await add_user(user)

    create_game(chat_id, user.id, user.first_name or "Unknown")
    lock_game(chat_id, "Mafia")

    game = get_game(chat_id)
    join_game(chat_id, user)

    game_started("Mafia", chat_id)

    sent = await message.reply_text(
        lobby_text(game),
        parse_mode=ParseMode.HTML,
        reply_markup=join_button(),
        disable_web_page_preview=True,
    )

    set_lobby_message(chat_id, sent.id)
    asyncio.create_task(join_countdown(client, chat_id))


async def mafia_rules_cmd(client, message: Message):
    await message.reply_text(
        rules_text(),
        parse_mode=ParseMode.HTML,
        reply_to_message_id=message.id,
        disable_web_page_preview=True,
    )


async def join_cmd(client, message: Message):
    chat_id = message.chat.id
    user = message.from_user

    if not user:
        return

    game = get_game(chat_id)
    if not game or game["status"] != "joining":
        return

    await add_user(user)
    ok, reason = join_game(chat_id, user)

    if not ok:
        if reason == "joined":
            await message.reply_text("You're already inside the game, darling~")
        elif reason == "full":
            await message.reply_text("The Mafia table is already full.")
        return

    await update_lobby_message(client, chat_id)
    try:
        await message.delete()
    except Exception:
        pass


# ──────────────────────────────────────────────
#  Lobby & Countdown
# ──────────────────────────────────────────────

async def join_countdown(client, chat_id: int):
    await asyncio.sleep(max(JOIN_TIME - 15, 1))

    game = get_game(chat_id)
    if not game or game["status"] != "joining":
        return

    await client.send_message(
        chat_id,
        join_countdown_text(15),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

    await asyncio.sleep(15)

    game = get_game(chat_id)
    if not game or game["status"] != "joining":
        return

    if len(game["players"]) < MIN_PLAYERS:
        await client.send_message(
            chat_id,
            not_enough_text(game),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
        end_game(chat_id)
        unlock_game(chat_id)
        return

    assign_roles(chat_id)
    await send_role_cards(client, chat_id)
    await start_night_phase(client, chat_id)


# ──────────────────────────────────────────────
#  Role Cards
# ──────────────────────────────────────────────

async def send_role_cards(client, chat_id: int):
    game = get_game(chat_id)
    if not game:
        return

    for user_id, player in game["players"].items():
        try:
            await client.send_message(
                user_id,
                role_guide(player["role"]),
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
        except Exception:
            await client.send_message(
                chat_id,
                no_dm_text(player["name"]),
                parse_mode=ParseMode.HTML,
            )


# ──────────────────────────────────────────────
#  Night Phase
# ──────────────────────────────────────────────

async def start_night_phase(client, chat_id: int):
    game = get_game(chat_id)
    if not game or game["status"] != "night":
        return

    await mafia_send(
        client,
        chat_id,
        night_group_text(game),
        gif=config.MAFIA_NIGHT_GIF,
    )

    await send_night_action_dms(client, chat_id)
    asyncio.create_task(night_timer(client, chat_id, game["day"]))


async def send_night_action_dms(client, chat_id: int):
    game = get_game(chat_id)
    if not game:
        return

    for user_id, player in game["players"].items():
        if user_id not in game["alive"]:
            continue

        role = player["role"]

        try:
            if role in ("mafia", "godfather"):
                await client.send_message(
                    user_id,
                    mafia_action_dm(game),
                    parse_mode=ParseMode.HTML,
                    reply_markup=mafia_kill_buttons(game, user_id),
                    disable_web_page_preview=True,
                )

            elif role == "doctor":
                await client.send_message(
                    user_id,
                    doctor_action_dm(),
                    parse_mode=ParseMode.HTML,
                    reply_markup=doctor_save_buttons(game, user_id),
                    disable_web_page_preview=True,
                )

            elif role == "detective":
                await client.send_message(
                    user_id,
                    detective_action_dm(),
                    parse_mode=ParseMode.HTML,
                    reply_markup=detective_buttons(game, user_id),
                    disable_web_page_preview=True,
                )

            elif role == "bodyguard":
                await client.send_message(
                    user_id,
                    bodyguard_action_dm(),
                    parse_mode=ParseMode.HTML,
                    reply_markup=bodyguard_buttons(game, user_id),
                    disable_web_page_preview=True,
                )

            elif role == "cupid":
                # Cupid only acts on Night 1 and only if not yet done
                if game["day"] == 1 and not game["night_actions"].get("cupid_done"):
                    await client.send_message(
                        user_id,
                        cupid_action_dm(),
                        parse_mode=ParseMode.HTML,
                        reply_markup=cupid_first_pick_buttons(game),
                        disable_web_page_preview=True,
                    )
                else:
                    await client.send_message(
                        user_id,
                        villager_night_dm(role),
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True,
                    )

            elif role == "vigilante":
                await client.send_message(
                    user_id,
                    (
                        "<blockquote>🔫 <b>Midnight Gunner</b></blockquote>\n\n"
                        "<i>❝ One bullet. One choice. One mistake can ruin the town. ♡ ❞</i>\n\n"
                        "Choose someone to shoot tonight."
                    ),
                    parse_mode=ParseMode.HTML,
                    reply_markup=vigilante_buttons(game, user_id),
                    disable_web_page_preview=True,
                )

            elif role == "witch":
                save_used = player.get("witch_save_used", False)
                kill_used = player.get("witch_kill_used", False)

                if save_used and kill_used:
                    await client.send_message(
                        user_id,
                        (
                            "<blockquote>🧙 <b>Velvet Witch</b></blockquote>\n\n"
                            "<i>❝ Your bottles are empty now, darling. Magic always has a price. ♡ ❞</i>\n\n"
                            "Both potions have already been used. You have no night action left."
                        ),
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True,
                    )
                else:
                    await client.send_message(
                        user_id,
                        (
                            "<blockquote>🧙 <b>Velvet Witch</b></blockquote>\n\n"
                            "<i>❝ Two potions. One mercy. One murder. Use them beautifully. ♡ ❞</i>\n\n"
                            f"🧪 Save Potion: {'<s>Used</s>' if save_used else '<b>Available</b>'}\n"
                            f"🩸 Kill Potion: {'<s>Used</s>' if kill_used else '<b>Available</b>'}\n\n"
                            "Choose your potion."
                        ),
                        parse_mode=ParseMode.HTML,
                        reply_markup=witch_buttons(game, user_id),
                        disable_web_page_preview=True,
                    )

            elif role == "silencer":
                await client.send_message(
                    user_id,
                    (
                        "<blockquote>🎭 <b>Silence Broker</b></blockquote>\n\n"
                        "<i>❝ Some voices are too dangerous to let sunrise hear them. ♡ ❞</i>\n\n"
                        "Choose someone to silence tomorrow."
                    ),
                    parse_mode=ParseMode.HTML,
                    reply_markup=silencer_buttons(game, user_id),
                    disable_web_page_preview=True,
                )

            elif role == "arsonist":
                await client.send_message(
                    user_id,
                    (
                        "<blockquote>🔥 <b>Flame Gambler</b></blockquote>\n\n"
                        "<i>❝ Mark them quietly. Burn them when the table is ready. ♡ ❞</i>\n\n"
                        "Choose a player to mark, or ignite all marked players."
                    ),
                    parse_mode=ParseMode.HTML,
                    reply_markup=arsonist_buttons(game, user_id),
                    disable_web_page_preview=True,
                )

            else:
                # villager, mayor, jester, medium, undertaker, trickster (night)
                await client.send_message(
                    user_id,
                    villager_night_dm(role),
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )

        except Exception:
            await client.send_message(
                chat_id,
                no_dm_text(player["name"]),
                parse_mode=ParseMode.HTML,
            )


# ──────────────────────────────────────────────
#  Night Timer & Resolution
# ──────────────────────────────────────────────

async def night_timer(client, chat_id: int, day: int):
    await asyncio.sleep(NIGHT_TIME)

    game = get_game(chat_id)
    if not game or game["status"] != "night" or game["day"] != day:
        return

    result = resolve_night(chat_id)
    game = get_game(chat_id)

    # Notify special roles first (before the public announcement)
    await send_undertaker_reports(client, game, result)
    await send_medium_death_report(client, game, result)

    # Open last-words DM window — players have LAST_WORDS_TIME seconds to respond
    await send_last_words_prompts(client, game, result)

    winner = check_winner(chat_id)
    if winner:
        await finish_game(client, chat_id, winner)
        return

    await mafia_send(
        client,
        chat_id,
        discussion_text(game, result),
        gif=config.MAFIA_DAY_GIF,
    )

    asyncio.create_task(discussion_timer(client, chat_id, game["day"]))


# ──────────────────────────────────────────────
#  Last Words  ← PRIMARY BUG FIX
# ──────────────────────────────────────────────

async def send_last_words_prompts(client, game: dict, result: dict):
    """
    DM every player who died this phase asking for last words.
    kill_player() already populated game["last_words_waiting"] when each
    player was killed, so we just need to send the notification DM here.
    """
    dead_players = []

    for key in ("killed", "bodyguard_dead", "vigilante_killed", "witch_killed", "lover_dead"):
        p = result.get(key)
        if p:
            dead_players.append(p)

    for p in result.get("arson_killed", []):
        dead_players.append(p)

    for player in dead_players:
        pid = player.get("id")
        if not pid:
            continue
        # Only send if the window is still open (kill_player set it)
        if pid not in game.get("last_words_waiting", {}):
            continue
        try:
            await client.send_message(
                pid,
                (
                    "<blockquote>⚰️ <b>Your Final Moment</b></blockquote>\n\n"
                    "You have died.\n\n"
                    "If you have any last words, send them now.\n\n"
                    f"⏳ You have <b>30 seconds</b>.\n\n"
                    "<i>Whatever you write will be shown to the village.</i>"
                ),
                parse_mode=ParseMode.HTML,
            )
        except Exception:
            pass


async def mafia_last_words_dm(client, message: Message):
    """
    Handles private messages from dead players within their last-words window.
    BUG FIX: previously the function relied on game object comparison that
    could silently fail. Now uses the 'used' flag inside last_words_waiting.
    """
    user = message.from_user

    if not user or not message.text:
        return
    if message.chat.type != ChatType.PRIVATE:
        return
    if message.text.startswith("/"):
        return

    game = can_send_last_words(user.id)
    if not game:
        return

    text = message.text.strip()
    if len(text) > 250:
        text = text[:250] + "…"

    # Mark used BEFORE sending so a second message in the window is ignored
    mark_last_words_used(game, user.id)

    player = game["players"].get(user.id)
    if not player:
        return

    chat_id = game["chat_id"]

    # Forward last words to the group
    try:
        await client.send_message(
            chat_id,
            (
                "<blockquote>⚰️ <b>Last Words</b></blockquote>\n\n"
                f"<b>{player['name']}</b> whispered before silence:\n\n"
                f"<i>❝ {text} ❞</i>"
            ),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
    except Exception:
        pass

    # Also whisper to the Medium if alive
    medium_id = get_alive_role(game, "medium")
    if medium_id:
        try:
            await client.send_message(
                medium_id,
                (
                    "<blockquote>👻 <b>Grave Whisperer</b></blockquote>\n\n"
                    f"The dead whispered something…\n\n"
                    f"<b>{player['name']}:</b>\n"
                    f"<i>❝ {text} ❞</i>"
                ),
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
        except Exception:
            pass

    await message.reply_text("✅ Your last words were delivered to the village.")


# ──────────────────────────────────────────────
#  Special Role Reports (Undertaker / Medium)
# ──────────────────────────────────────────────

async def send_undertaker_reports(client, game: dict, result: dict):
    undertaker_id = get_alive_role(game, "undertaker")
    if not undertaker_id:
        return

    dead_players = []
    for key in ("killed", "bodyguard_dead", "vigilante_killed", "witch_killed", "lover_dead"):
        p = result.get(key)
        if p:
            dead_players.append(p)
    for p in result.get("arson_killed", []):
        dead_players.append(p)

    if not dead_players:
        return

    lines = [
        f"• <b>{p['name']}</b> → {role_name(p['role'])}"
        for p in dead_players
    ]

    try:
        await client.send_message(
            undertaker_id,
            (
                "<blockquote>⚰️ <b>Soul Keeper Report</b></blockquote>\n\n"
                + "\n".join(lines)
            ),
            parse_mode=ParseMode.HTML,
        )
    except Exception:
        pass


async def send_medium_death_report(client, game: dict, result: dict):
    medium_id = get_alive_role(game, "medium")
    if not medium_id:
        return

    lines = []
    if result.get("killed"):
        lines.append(f"💀 {result['killed']['name']} was taken by the shadows.")
    if result.get("bodyguard_dead"):
        lines.append(f"🛡 {result['bodyguard_dead']['name']} died protecting someone.")
    if result.get("vigilante_killed"):
        lines.append(f"🔫 {result['vigilante_killed']['name']} was shot.")
    if result.get("witch_killed"):
        lines.append(f"🩸 {result['witch_killed']['name']} was poisoned.")
    if result.get("arson_killed"):
        names = ", ".join(p["name"] for p in result["arson_killed"])
        lines.append(f"🔥 Burned: {names}")
    if result.get("lover_dead"):
        lines.append(f"💔 {result['lover_dead']['name']} died from heartbreak.")

    if not lines:
        lines.append("🌙 The dead were silent tonight.")

    try:
        await client.send_message(
            medium_id,
            (
                "<blockquote>👻 <b>Grave Whisperer Report</b></blockquote>\n\n"
                "<i>❝ The dead are restless tonight… ♡ ❞</i>\n\n"
                + "\n".join(lines)
            ),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
    except Exception:
        pass


# ──────────────────────────────────────────────
#  Discussion & Vote Timers
# ──────────────────────────────────────────────

async def discussion_timer(client, chat_id: int, day: int):
    await asyncio.sleep(DISCUSSION_TIME)

    game = get_game(chat_id)
    if not game or game["status"] != "discussion" or game["day"] != day:
        return

    start_voting(chat_id)
    game = get_game(chat_id)

    await mafia_send(
        client,
        chat_id,
        voting_text(game),
        gif=config.MAFIA_VOTING_GIF,
        reply_markup=voting_buttons(game),
    )

    # Notify Trickster if alive and unused
    game = get_game(chat_id)
    for user_id, player in game["players"].items():
        if player["role"] == "trickster" and player["alive"] and not player.get("trickster_used"):
            try:
                await client.send_message(
                    user_id,
                    (
                        "<blockquote>🃏 <b>Fate Trickster</b></blockquote>\n\n"
                        "<i>❝ The vote is a little too honest. Shall we ruin it? ♡ ❞</i>\n\n"
                        "You may secretly swap the top 2 vote counts — once per game."
                    ),
                    parse_mode=ParseMode.HTML,
                    reply_markup=trickster_vote_button(),
                )
            except Exception:
                pass

    asyncio.create_task(vote_timer(client, chat_id, game["day"]))


async def vote_timer(client, chat_id: int, day: int):
    await asyncio.sleep(VOTE_TIME)

    game = get_game(chat_id)
    if not game or game["status"] != "voting" or game["day"] != day:
        return

    await apply_vote_afk(client, chat_id)

    result = resolve_votes(chat_id)
    game = get_game(chat_id)

    # Notify special roles about vote eliminations
    await send_last_words_prompts(client, game, result)
    await send_undertaker_reports(client, game, result)
    await send_medium_death_report(client, game, result)

    await mafia_send(
        client,
        chat_id,
        vote_result_text(game, result),
        gif=config.MAFIA_DEATH_GIF,
    )

    if result and result.get("jester_win"):
        await finish_game(client, chat_id, "jester")
        return

    winner = check_winner(chat_id)
    if winner:
        await finish_game(client, chat_id, winner)
        return

    await start_night_phase(client, chat_id)


# ──────────────────────────────────────────────
#  Finish Game
# ──────────────────────────────────────────────

async def finish_game(client, chat_id: int, winner: str):
    game = get_game(chat_id)
    if not game:
        return

    mvp = calculate_mvp(game, winner)
    await reward_game(chat_id, winner)

    gif = config.MAFIA_JESTER_GIF if winner == "jester" else config.MAFIA_WIN_GIF

    await client.send_animation(
        chat_id,
        gif,
        winner_text(game, winner, mvp),
        parse_mode=ParseMode.HTML,
    )

    game_finished("Mafia", winner)
    end_game(chat_id)
    unlock_game(chat_id)


# ──────────────────────────────────────────────
#  Silencer: Block silenced player's messages
# ──────────────────────────────────────────────

async def silenced_message_blocker(client, message: Message):
    if not message.from_user:
        return
    if message.chat.type == ChatType.PRIVATE:
        return

    game = get_game(message.chat.id)
    if not game or game.get("status") != "discussion":
        return

    silenced_user = game.get("night_actions", {}).get("silenced")
    if not silenced_user or message.from_user.id != silenced_user:
        return

    try:
        await message.delete()
    except Exception:
        pass

    try:
        await client.send_message(
            message.from_user.id,
            (
                "<blockquote>🎭 <b>You Are Silenced</b></blockquote>\n\n"
                "The Silence Broker chose you last night.\n\n"
                "You cannot speak, send media, stickers, GIFs, "
                "voice notes, or commands during this day phase."
            ),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
    except Exception:
        pass


# ──────────────────────────────────────────────
#  Callback: Join
# ──────────────────────────────────────────────

async def mafia_join_callback(client, query: CallbackQuery):
    chat_id = query.message.chat.id
    user = query.from_user

    game = get_game(chat_id)
    if not game or game["status"] != "joining":
        await query.answer("No open Mafia lobby.", show_alert=True)
        return

    await add_user(user)
    ok, reason = join_game(chat_id, user)

    if not ok:
        msgs = {
            "joined": "You're already inside, darling~",
            "full": "The table is full.",
            "dead_player": "Dead players cannot rejoin this match.",
        }
        await query.answer(msgs.get(reason, "You cannot join now."), show_alert=True)
        return

    await query.answer("You joined Mafia! Check your DMs for your role card.")
    await update_lobby_message(client, chat_id)


# ──────────────────────────────────────────────
#  Callback: Mafia Kill  ← BUG FIX (removed __import__ hack)
# ──────────────────────────────────────────────

async def mafia_kill_callback(client, query: CallbackQuery):
    user = query.from_user
    chat_id = find_user_game(user.id)

    if not chat_id:
        await query.answer("No Mafia game found.", show_alert=True)
        return

    target_id = int(query.data.replace("mf_kill_", "", 1))
    ok, reason = mafia_vote(chat_id, user.id, target_id)

    if not ok:
        await query.answer(reason, show_alert=True)
        return

    await query.message.edit_text(
        action_saved_text("🔪 Victim selected."),
        parse_mode=ParseMode.HTML,
    )
    await query.answer("Victim selected.")


# ──────────────────────────────────────────────
#  Callbacks: Town Roles
# ──────────────────────────────────────────────

async def doctor_save_callback(client, query: CallbackQuery):
    user = query.from_user
    chat_id = find_user_game(user.id)

    if not chat_id:
        await query.answer("No Mafia game found.", show_alert=True)
        return

    target_id = int(query.data.replace("mf_save_", "", 1))
    ok, reason = doctor_save(chat_id, user.id, target_id)

    if not ok:
        await query.answer(reason, show_alert=True)
        return

    await query.message.edit_text(
        action_saved_text("🩺 Protection chosen."),
        parse_mode=ParseMode.HTML,
    )
    await query.answer("Protection selected.")


async def detective_check_callback(client, query: CallbackQuery):
    user = query.from_user
    chat_id = find_user_game(user.id)

    if not chat_id:
        await query.answer("No Mafia game found.", show_alert=True)
        return

    target_id = int(query.data.replace("mf_check_", "", 1))
    ok, reason, is_mafia = detective_check(chat_id, user.id, target_id)

    if not ok:
        await query.answer(reason, show_alert=True)
        return

    game = get_game(chat_id)
    target = get_player(game, target_id)

    await query.message.edit_text(
        detective_result_text(target["name"], is_mafia),
        parse_mode=ParseMode.HTML,
    )
    await query.answer("Investigation complete.")


async def bodyguard_callback(client, query: CallbackQuery):
    user = query.from_user
    chat_id = find_user_game(user.id)

    if not chat_id:
        await query.answer("No Mafia game found.", show_alert=True)
        return

    target_id = int(query.data.replace("mf_guard_", "", 1))
    ok, reason = bodyguard_protect(chat_id, user.id, target_id)

    if not ok:
        await query.answer(reason, show_alert=True)
        return

    await query.message.edit_text(
        action_saved_text("🛡 Guard target selected."),
        parse_mode=ParseMode.HTML,
    )
    await query.answer("Guard selected.")


async def cupid_first_callback(client, query: CallbackQuery):
    user = query.from_user
    chat_id = find_user_game(user.id)

    if not chat_id:
        await query.answer("No Mafia game found.", show_alert=True)
        return

    first_id = int(query.data.replace("mf_cupid1_", "", 1))
    game = get_game(chat_id)
    first = get_player(game, first_id)

    await query.message.edit_text(
        cupid_second_text(first["name"]),
        parse_mode=ParseMode.HTML,
        reply_markup=cupid_second_pick_buttons(game, first_id),
    )
    await query.answer("First lover selected.")


async def cupid_second_callback(client, query: CallbackQuery):
    user = query.from_user
    chat_id = find_user_game(user.id)

    if not chat_id:
        await query.answer("No Mafia game found.", show_alert=True)
        return

    data = query.data.replace("mf_cupid2_", "", 1)
    first_id, second_id = map(int, data.split("_", 1))

    ok, reason = cupid_link(chat_id, user.id, first_id, second_id)

    if not ok:
        await query.answer(reason, show_alert=True)
        return

    await query.message.edit_text(
        action_saved_text("❤️ Lovers linked."),
        parse_mode=ParseMode.HTML,
    )
    await query.answer("Lovers linked.")


async def vote_callback(client, query: CallbackQuery):
    chat_id = query.message.chat.id
    user = query.from_user

    raw = query.data.replace("mf_vote_", "", 1)
    target_id = "skip" if raw == "skip" else int(raw)

    ok, reason = vote_player(chat_id, user.id, target_id)

    if not ok:
        await query.answer(reason, show_alert=True)
        return

    if target_id == "skip":
        target_name = "Skip Vote"
    else:
        game = get_game(chat_id)
        target = get_player(game, target_id)
        target_name = target["name"] if target else "Unknown"

    await query.answer("Vote recorded.")
    await query.message.reply_text(
        vote_recorded_text(target_name),
        parse_mode=ParseMode.HTML,
    )


# ──────────────────────────────────────────────
#  Callbacks: Vigilante / Witch / Silencer / Arsonist / Trickster
# ──────────────────────────────────────────────

async def vigilante_callback(client, query: CallbackQuery):
    user = query.from_user
    chat_id = find_user_game(user.id)

    if not chat_id:
        await query.answer("No Mafia game found.", show_alert=True)
        return

    target_id = int(query.data.replace("mf_vigi_", "", 1))
    ok, reason = vigilante_shoot(chat_id, user.id, target_id)

    if not ok:
        await query.answer(reason, show_alert=True)
        return

    await query.message.edit_text(
        action_saved_text("🔫 Shot target selected."),
        parse_mode=ParseMode.HTML,
    )
    await query.answer("Shot selected.")


async def witch_menu_callback(client, query: CallbackQuery):
    user = query.from_user
    chat_id = find_user_game(user.id)

    if not chat_id:
        await query.answer("No Mafia game found.", show_alert=True)
        return

    game = get_game(chat_id)

    if query.data == "mf_witch_kill_menu":
        await query.message.edit_text(
            "<blockquote>🩸 <b>Kill Potion</b></blockquote>\n\nChoose someone to poison.",
            parse_mode=ParseMode.HTML,
            reply_markup=witch_kill_buttons(game, user.id),
        )
    else:
        await query.message.edit_text(
            "<blockquote>🧪 <b>Save Potion</b></blockquote>\n\nChoose someone to protect.",
            parse_mode=ParseMode.HTML,
            reply_markup=witch_save_buttons(game, user.id),
        )
    await query.answer()


async def witch_kill_callback(client, query: CallbackQuery):
    user = query.from_user
    chat_id = find_user_game(user.id)

    if not chat_id:
        await query.answer("No Mafia game found.", show_alert=True)
        return

    target_id = int(query.data.replace("mf_witchkill_", "", 1))
    ok, reason = witch_kill(chat_id, user.id, target_id)

    if not ok:
        await query.answer(reason, show_alert=True)
        return

    await query.message.edit_text(
        action_saved_text("🩸 Kill potion used."),
        parse_mode=ParseMode.HTML,
    )
    await query.answer("Kill potion used.")


async def witch_save_callback(client, query: CallbackQuery):
    user = query.from_user
    chat_id = find_user_game(user.id)

    if not chat_id:
        await query.answer("No Mafia game found.", show_alert=True)
        return

    target_id = int(query.data.replace("mf_witchsave_", "", 1))
    ok, reason = witch_save(chat_id, user.id, target_id)

    if not ok:
        await query.answer(reason, show_alert=True)
        return

    await query.message.edit_text(
        action_saved_text("🧪 Save potion used."),
        parse_mode=ParseMode.HTML,
    )
    await query.answer("Save potion used.")


async def witch_empty_callback(client, query: CallbackQuery):
    await query.answer(
        "Your potions are already used, darling~",
        show_alert=True,
    )


async def silencer_callback(client, query: CallbackQuery):
    user = query.from_user
    chat_id = find_user_game(user.id)

    if not chat_id:
        await query.answer("No Mafia game found.", show_alert=True)
        return

    target_id = int(query.data.replace("mf_silence_", "", 1))
    ok, reason = silence_player(chat_id, user.id, target_id)

    if not ok:
        await query.answer(reason, show_alert=True)
        return

    await query.message.edit_text(
        action_saved_text("🎭 Target silenced."),
        parse_mode=ParseMode.HTML,
    )
    await query.answer("Silenced.")


async def arson_mark_callback(client, query: CallbackQuery):
    user = query.from_user
    chat_id = find_user_game(user.id)

    if not chat_id:
        await query.answer("No Mafia game found.", show_alert=True)
        return

    target_id = int(query.data.replace("mf_arsonmark_", "", 1))
    ok, reason = arsonist_mark(chat_id, user.id, target_id)

    if not ok:
        await query.answer(reason, show_alert=True)
        return

    await query.message.edit_text(
        action_saved_text("🔥 Target marked."),
        parse_mode=ParseMode.HTML,
    )
    await query.answer("Marked.")


async def arson_ignite_callback(client, query: CallbackQuery):
    user = query.from_user
    chat_id = find_user_game(user.id)

    if not chat_id:
        await query.answer("No Mafia game found.", show_alert=True)
        return

    ok, reason = arsonist_ignite(chat_id, user.id)

    if not ok:
        await query.answer(reason, show_alert=True)
        return

    await query.message.edit_text(
        action_saved_text("🔥 Flames prepared. They will burn at night's end."),
        parse_mode=ParseMode.HTML,
    )
    await query.answer("Ignite prepared.")


async def trickster_callback(client, query: CallbackQuery):
    chat_id = find_user_game(query.from_user.id)

    if not chat_id:
        await query.answer("No Mafia game found.", show_alert=True)
        return

    ok, reason = trickster_twist(chat_id, query.from_user.id)

    if not ok:
        await query.answer(reason, show_alert=True)
        return

    await query.message.edit_text(
        action_saved_text("🃏 Vote twist activated. The top two counts will be swapped."),
        parse_mode=ParseMode.HTML,
    )
    await query.answer("The vote has been twisted.")


# ──────────────────────────────────────────────
#  Handler Registration
# ──────────────────────────────────────────────

def register_mafia_handlers(app):
    # Commands
    app.add_handler(
        MessageHandler(mafia_cmd, filters.command(["mafia", "startmafia"]) & filters.group),
        group=180,
    )
    app.add_handler(
        MessageHandler(mafia_rules_cmd, filters.command(["mafiarules", "mafiahelp"])),
        group=180,
    )
    app.add_handler(
        MessageHandler(join_cmd, filters.command("join") & filters.group),
        group=180,
    )

    # Last words — must be registered BEFORE generic private handlers
    app.add_handler(
        MessageHandler(mafia_last_words_dm, filters.private & filters.text & ~filters.command([])),
        group=179,
    )

    # Lobby join button
    app.add_handler(
        CallbackQueryHandler(mafia_join_callback, filters.regex("^mafia_join$")),
        group=180,
    )

    # Night action callbacks
    app.add_handler(CallbackQueryHandler(mafia_kill_callback,       filters.regex("^mf_kill_")),           group=181)
    app.add_handler(CallbackQueryHandler(doctor_save_callback,      filters.regex("^mf_save_")),           group=181)
    app.add_handler(CallbackQueryHandler(detective_check_callback,  filters.regex("^mf_check_")),          group=181)
    app.add_handler(CallbackQueryHandler(bodyguard_callback,        filters.regex("^mf_guard_")),          group=181)
    app.add_handler(CallbackQueryHandler(cupid_first_callback,      filters.regex("^mf_cupid1_")),         group=181)
    app.add_handler(CallbackQueryHandler(cupid_second_callback,     filters.regex("^mf_cupid2_")),         group=181)
    app.add_handler(CallbackQueryHandler(vigilante_callback,        filters.regex("^mf_vigi_")),           group=181)
    app.add_handler(CallbackQueryHandler(witch_menu_callback,       filters.regex("^mf_witch_(kill|save)_menu$")), group=181)
    app.add_handler(CallbackQueryHandler(witch_kill_callback,       filters.regex("^mf_witchkill_")),      group=181)
    app.add_handler(CallbackQueryHandler(witch_save_callback,       filters.regex("^mf_witchsave_")),      group=181)
    app.add_handler(CallbackQueryHandler(witch_empty_callback,      filters.regex("^mf_witch_empty$")),    group=181)
    app.add_handler(CallbackQueryHandler(silencer_callback,         filters.regex("^mf_silence_")),        group=181)
    app.add_handler(CallbackQueryHandler(arson_mark_callback,       filters.regex("^mf_arsonmark_")),      group=181)
    app.add_handler(CallbackQueryHandler(arson_ignite_callback,     filters.regex("^mf_arsonignite$")),    group=181)
    app.add_handler(CallbackQueryHandler(trickster_callback,        filters.regex("^mf_trickster_twist$")), group=181)

    # Voting
    app.add_handler(CallbackQueryHandler(vote_callback, filters.regex("^mf_vote_")), group=181)

    # Silencer message blocker — low group number = high priority
    app.add_handler(
        MessageHandler(
            silenced_message_blocker,
            filters.group & ~filters.service,
        ),
        group=-250,
    )