# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
# ==========================================================

from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

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


def td_buttons():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🌙 Truth", callback_data="td_truth"),
                InlineKeyboardButton("🎲 Dare", callback_data="td_dare"),
            ],
            [
                InlineKeyboardButton("🎭 Random", callback_data="td_random"),
            ],
        ]
    )


def dare_buttons():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✅ Done", callback_data="td_done"),
                InlineKeyboardButton("❌ Skip", callback_data="td_skip"),
            ]
        ]
    )


async def truth_dare_cmd(client, message: Message):
    if not message.from_user:
        return

    await add_user(message.from_user)

    await message.reply_text(
        (
            "<blockquote>🎭 <b>Truth Or Dare</b></blockquote>\n\n"
            "<i>❝ Choose carefully, darling. Honesty and bravery both have a price. ♡ ❞</i>\n\n"
            "Pick your fate below."
        ),
        parse_mode=ParseMode.HTML,
        reply_markup=td_buttons(),
        reply_to_message_id=message.id,
        disable_web_page_preview=True,
    )


async def truth_callback(client, query: CallbackQuery):
    user = query.from_user
    chat_id = query.message.chat.id

    text = get_truth()
    create_truth_session(chat_id, user.id, text)

    await query.message.edit_text(
        (
            "<blockquote>🌙 <b>Truth</b></blockquote>\n\n"
            f"{text}\n\n"
            "<i>Reply to this question with your answer.</i>"
        ),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )
    await query.answer("Truth chosen.")


async def dare_callback(client, query: CallbackQuery):
    user = query.from_user
    chat_id = query.message.chat.id

    text = get_dare()
    create_dare_session(chat_id, user.id, text)

    await query.message.edit_text(
        (
            "<blockquote>🎲 <b>Dare</b></blockquote>\n\n"
            f"{text}\n\n"
            "<i>Complete it and press Done, or skip if fate scares you.</i>"
        ),
        parse_mode=ParseMode.HTML,
        reply_markup=dare_buttons(),
        disable_web_page_preview=True,
    )
    await query.answer("Dare chosen.")


async def random_callback(client, query: CallbackQuery):
    user = query.from_user
    chat_id = query.message.chat.id

    kind, text = get_random_truth_dare()

    if kind == "truth":
        create_truth_session(chat_id, user.id, text)
        title = "🌙 <b>Truth</b>"
        ending = "<i>Reply to this question with your answer.</i>"
        markup = None
    else:
        create_dare_session(chat_id, user.id, text)
        title = "🎲 <b>Dare</b>"
        ending = "<i>Complete it and press Done, or skip if fate scares you.</i>"
        markup = dare_buttons()

    await query.message.edit_text(
        f"<blockquote>{title}</blockquote>\n\n{text}\n\n{ending}",
        parse_mode=ParseMode.HTML,
        reply_markup=markup,
        disable_web_page_preview=True,
    )
    await query.answer("Fate has chosen.")


async def dare_done_callback(client, query: CallbackQuery):
    user = query.from_user
    chat_id = query.message.chat.id

    session = get_session(chat_id, user.id)

    if not session or session["type"] != "dare":
        await query.answer("No active dare found for you.", show_alert=True)
        return

    await add_xp(user.id, DARE_XP)
    await add_coins(user.id, DARE_COINS)
    remove_session(chat_id, user.id)

    await query.message.edit_text(
        (
            f"{random_dare_complete_reaction()}\n\n"
            f"✨ XP: +<b>{DARE_XP}</b>\n"
            f"💰 Coins: +<b>{DARE_COINS}</b>"
        ),
        parse_mode=ParseMode.HTML,
    )
    await query.answer("Dare completed.")


async def dare_skip_callback(client, query: CallbackQuery):
    user = query.from_user
    chat_id = query.message.chat.id

    session = get_session(chat_id, user.id)

    if not session or session["type"] != "dare":
        await query.answer("No active dare found for you.", show_alert=True)
        return

    remove_session(chat_id, user.id)

    await query.message.edit_text(
        random_dare_skip_reaction(),
        parse_mode=ParseMode.HTML,
    )
    await query.answer("Skipped.")


async def truth_answer_checker(client, message: Message):
    if not message.from_user or not message.text:
        return

    if message.text.startswith("/"):
        return

    session = get_session(message.chat.id, message.from_user.id)

    if not session or session["type"] != "truth":
        return

    await add_xp(message.from_user.id, TRUTH_XP)
    remove_session(message.chat.id, message.from_user.id)

    await message.reply_text(
        (
            f"{random_truth_reaction()}\n\n"
            f"✨ XP: +<b>{TRUTH_XP}</b>"
        ),
        parse_mode=ParseMode.HTML,
        reply_to_message_id=message.id,
    )


def register_truth_dare_handlers(app):
    app.add_handler(
        MessageHandler(
            truth_dare_cmd,
            filters.command(["truthdare", "td", "truthordare"]) & filters.group,
        ),
        group=210,
    )

    app.add_handler(
        CallbackQueryHandler(truth_callback, filters.regex("^td_truth$")),
        group=210,
    )

    app.add_handler(
        CallbackQueryHandler(dare_callback, filters.regex("^td_dare$")),
        group=210,
    )

    app.add_handler(
        CallbackQueryHandler(random_callback, filters.regex("^td_random$")),
        group=210,
    )

    app.add_handler(
        CallbackQueryHandler(dare_done_callback, filters.regex("^td_done$")),
        group=210,
    )

    app.add_handler(
        CallbackQueryHandler(dare_skip_callback, filters.regex("^td_skip$")),
        group=210,
    )

    app.add_handler(
        MessageHandler(
            truth_answer_checker,
            filters.text & filters.group,
        ),
        group=-20,
    )