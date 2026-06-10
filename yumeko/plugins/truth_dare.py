# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
#
#  Developer  : Jass
#  Project    : Yumeko Games Bot
#  Version    : 1.0.0
#
#  GitHub     : Private
#  License    : MIT License
#
#  This file is part of Yumeko Games Bot.
#  Unauthorized removal of this notice is discouraged.
#
#  © 2026 Jass. All Rights Reserved.
# ==========================================================

import html

from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from yumeko.client import app
from yumeko.database.users import add_user, add_xp, add_coins
from yumeko.games.party.truth_dare import (
    TRUTH_XP,
    DARE_XP,
    DARE_COINS,
    get_truth,
    get_dare,
    get_random_truth_dare,
    create_truth_session,
    create_dare_session,
    get_session,
    remove_session,
    random_truth_reaction,
    random_dare_complete_reaction,
    random_dare_skip_reaction,
)
from yumeko.locales import get_text


def mention_user(user):
    if not user:
        return "Player"

    name = html.escape(user.first_name or "Player")
    return f'<a href="tg://user?id={user.id}">{name}</a>'


def get_target_user(message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user

    return message.from_user


def truth_dare_buttons(user_id: int):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    get_text("btn_truth"),
                    callback_data=f"td_truth_{user_id}",
                ),
                InlineKeyboardButton(
                    get_text("btn_dare"),
                    callback_data=f"td_dare_{user_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    get_text("btn_random_td"),
                    callback_data=f"td_random_{user_id}",
                ),
            ],
        ]
    )


def dare_action_buttons(user_id: int):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    get_text("btn_dare_done"),
                    callback_data=f"td_done_{user_id}",
                ),
                InlineKeyboardButton(
                    get_text("btn_dare_skip"),
                    callback_data=f"td_skip_{user_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    get_text("btn_random_td"),
                    callback_data=f"td_random_{user_id}",
                ),
            ],
        ]
    )


async def send_truth(message: Message, target):
    await add_user(target)

    question = get_truth()
    create_truth_session(message.chat.id, target.id, question)

    await message.reply_text(
        get_text(
            "truth_caption",
            mention=mention_user(target),
            question=html.escape(question),
            xp=TRUTH_XP,
        ),
        parse_mode=ParseMode.HTML,
        reply_markup=truth_dare_buttons(target.id),
        reply_to_message_id=message.reply_to_message.id
        if message.reply_to_message
        else message.id,
        disable_web_page_preview=True,
    )


async def send_dare(message: Message, target):
    await add_user(target)

    dare = get_dare()
    create_dare_session(message.chat.id, target.id, dare)

    await message.reply_text(
        get_text(
            "dare_caption",
            mention=mention_user(target),
            dare=html.escape(dare),
            coins=DARE_COINS,
            xp=DARE_XP,
        ),
        parse_mode=ParseMode.HTML,
        reply_markup=dare_action_buttons(target.id),
        reply_to_message_id=message.reply_to_message.id
        if message.reply_to_message
        else message.id,
        disable_web_page_preview=True,
    )


async def edit_truth(query: CallbackQuery, target_user):
    question = get_truth()
    create_truth_session(query.message.chat.id, target_user.id, question)

    await query.message.edit_text(
        get_text(
            "truth_caption",
            mention=mention_user(target_user),
            question=html.escape(question),
            xp=TRUTH_XP,
        ),
        parse_mode=ParseMode.HTML,
        reply_markup=truth_dare_buttons(target_user.id),
        disable_web_page_preview=True,
    )


async def edit_dare(query: CallbackQuery, target_user):
    dare = get_dare()
    create_dare_session(query.message.chat.id, target_user.id, dare)

    await query.message.edit_text(
        get_text(
            "dare_caption",
            mention=mention_user(target_user),
            dare=html.escape(dare),
            coins=DARE_COINS,
            xp=DARE_XP,
        ),
        parse_mode=ParseMode.HTML,
        reply_markup=dare_action_buttons(target_user.id),
        disable_web_page_preview=True,
    )


@app.on_message(filters.command("truth"))
async def truth_cmd(_, message: Message):
    target = get_target_user(message)
    await send_truth(message, target)


@app.on_message(filters.command("dare"))
async def dare_cmd(_, message: Message):
    target = get_target_user(message)
    await send_dare(message, target)


@app.on_message(filters.command(["truthdare", "td"]))
async def truthdare_cmd(_, message: Message):
    target = get_target_user(message)
    await add_user(target)

    mode, text = get_random_truth_dare()

    if mode == "truth":
        create_truth_session(message.chat.id, target.id, text)
        await message.reply_text(
            get_text(
                "truth_caption",
                mention=mention_user(target),
                question=html.escape(text),
                xp=TRUTH_XP,
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=truth_dare_buttons(target.id),
            reply_to_message_id=message.reply_to_message.id
            if message.reply_to_message
            else message.id,
            disable_web_page_preview=True,
        )
    else:
        create_dare_session(message.chat.id, target.id, text)
        await message.reply_text(
            get_text(
                "dare_caption",
                mention=mention_user(target),
                dare=html.escape(text),
                coins=DARE_COINS,
                xp=DARE_XP,
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=dare_action_buttons(target.id),
            reply_to_message_id=message.reply_to_message.id
            if message.reply_to_message
            else message.id,
            disable_web_page_preview=True,
        )


@app.on_callback_query(filters.regex("^td_truth_"))
async def td_truth_callback(_, query: CallbackQuery):
    user_id = int(query.data.split("_")[-1])

    if query.from_user.id != user_id:
        await query.answer(get_text("truthdare_not_yours"), show_alert=True)
        return

    await add_user(query.from_user)
    await edit_truth(query, query.from_user)
    await query.answer("Truth chosen.")


@app.on_callback_query(filters.regex("^td_dare_"))
async def td_dare_callback(_, query: CallbackQuery):
    user_id = int(query.data.split("_")[-1])

    if query.from_user.id != user_id:
        await query.answer(get_text("truthdare_not_yours"), show_alert=True)
        return

    await add_user(query.from_user)
    await edit_dare(query, query.from_user)
    await query.answer("Dare chosen.")


@app.on_callback_query(filters.regex("^td_random_"))
async def td_random_callback(_, query: CallbackQuery):
    user_id = int(query.data.split("_")[-1])

    if query.from_user.id != user_id:
        await query.answer(get_text("truthdare_not_yours"), show_alert=True)
        return

    await add_user(query.from_user)

    mode, text = get_random_truth_dare()

    if mode == "truth":
        create_truth_session(query.message.chat.id, query.from_user.id, text)

        await query.message.edit_text(
            get_text(
                "truth_caption",
                mention=mention_user(query.from_user),
                question=html.escape(text),
                xp=TRUTH_XP,
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=truth_dare_buttons(query.from_user.id),
            disable_web_page_preview=True,
        )
        await query.answer("Truth chosen.")
        return

    create_dare_session(query.message.chat.id, query.from_user.id, text)

    await query.message.edit_text(
        get_text(
            "dare_caption",
            mention=mention_user(query.from_user),
            dare=html.escape(text),
            coins=DARE_COINS,
            xp=DARE_XP,
        ),
        parse_mode=ParseMode.HTML,
        reply_markup=dare_action_buttons(query.from_user.id),
        disable_web_page_preview=True,
    )
    await query.answer("Dare chosen.")


@app.on_callback_query(filters.regex("^td_done_"))
async def td_done_callback(_, query: CallbackQuery):
    user_id = int(query.data.split("_")[-1])

    if query.from_user.id != user_id:
        await query.answer(get_text("truthdare_not_yours"), show_alert=True)
        return

    session = get_session(query.message.chat.id, user_id)

    if not session or session["type"] != "dare":
        await query.answer(get_text("truthdare_no_active"), show_alert=True)
        return

    await add_user(query.from_user)
    await add_xp(user_id, DARE_XP)
    await add_coins(user_id, DARE_COINS)

    reaction = random_dare_complete_reaction()

    await query.message.edit_text(
        get_text(
            "dare_completed",
            reaction=reaction,
            coins=DARE_COINS,
            xp=DARE_XP,
        ),
        parse_mode=ParseMode.HTML,
        reply_markup=truth_dare_buttons(user_id),
        disable_web_page_preview=True,
    )

    remove_session(query.message.chat.id, user_id)
    await query.answer("Dare completed!")


@app.on_callback_query(filters.regex("^td_skip_"))
async def td_skip_callback(_, query: CallbackQuery):
    user_id = int(query.data.split("_")[-1])

    if query.from_user.id != user_id:
        await query.answer(get_text("truthdare_not_yours"), show_alert=True)
        return

    session = get_session(query.message.chat.id, user_id)

    if not session or session["type"] != "dare":
        await query.answer(get_text("truthdare_no_active"), show_alert=True)
        return

    reaction = random_dare_skip_reaction()

    await query.message.edit_text(
        get_text(
            "dare_skipped",
            reaction=reaction,
        ),
        parse_mode=ParseMode.HTML,
        reply_markup=truth_dare_buttons(user_id),
        disable_web_page_preview=True,
    )

    remove_session(query.message.chat.id, user_id)
    await query.answer("Skipped.")


@app.on_message(filters.text & filters.group)
async def truth_answer_checker(_, message: Message):
    if not message.from_user:
        return

    if message.text.startswith("/"):
        return

    user_id = message.from_user.id
    chat_id = message.chat.id

    session = get_session(chat_id, user_id)

    if not session:
        return

    if session["type"] != "truth":
        return

    await add_user(message.from_user)
    await add_xp(user_id, TRUTH_XP)

    reaction = random_truth_reaction()

    await message.reply_text(
        get_text(
            "truth_answered",
            reaction=reaction,
            xp=TRUTH_XP,
        ),
        parse_mode=ParseMode.HTML,
        reply_to_message_id=message.id,
        disable_web_page_preview=True,
    )

    remove_session(chat_id, user_id)