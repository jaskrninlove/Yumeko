# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
# ==========================================================

from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from yumeko.core.games_registry import (
    get_all_categories,
    get_game,
    paginated_games,
    GAMES_PER_PAGE,
)


def arcade_caption(category_id: str = "all", page: int = 0):
    category = get_all_categories().get(category_id, {"title": "🎮 Yumeko Arcade"})
    games, total = paginated_games(category_id, page)

    return (
        f"<blockquote>{category['title']}</blockquote>\n\n"
        f"<i>❝ Welcome to Yumeko’s Arcade, where every command opens a new table of thrill. ♡ ❞</i>\n\n"
        f"🎲 Entries: <b>{total}</b>\n"
        f"📄 Page: <b>{page + 1}</b>\n\n"
        f"Choose your game, darling."
    )


def arcade_buttons(category_id: str = "all", page: int = 0):
    rows = []
    games, total = paginated_games(category_id, page)

    temp = []
    for game_id, game in games:
        temp.append(
            InlineKeyboardButton(
                game["title"],
                callback_data=f"ygameinfo_{game_id}_{category_id}_{page}",
            )
        )

        if len(temp) == 2:
            rows.append(temp)
            temp = []

    if temp:
        rows.append(temp)

    nav = []

    if page > 0:
        nav.append(
            InlineKeyboardButton(
                "⬅️ Prev",
                callback_data=f"yumeko_page_{category_id}_{page - 1}",
            )
        )

    if (page + 1) * GAMES_PER_PAGE < total:
        nav.append(
            InlineKeyboardButton(
                "Next ➡️",
                callback_data=f"yumeko_page_{category_id}_{page + 1}",
            )
        )

    if nav:
        rows.append(nav)

    rows.append(
        [
            InlineKeyboardButton(
                "🗂 Categories",
                callback_data="yumeko_categories",
            )
        ]
    )

    return InlineKeyboardMarkup(rows)

def categories_buttons():
    rows = []
    temp = []

    for cid, cat in get_all_categories().items():
        temp.append(
            InlineKeyboardButton(
                cat["title"],
                callback_data=f"yumeko_page_{cid}_0",
            )
        )

        if len(temp) == 2:
            rows.append(temp)
            temp = []

    if temp:
        rows.append(temp)

    rows.append(
        [
            InlineKeyboardButton(
                "⬅️ Back To Arcade",
                callback_data="yumeko_page_all_0",
            )
        ]
    )

    return InlineKeyboardMarkup(rows)

async def yumeko_categories_callback(client, query: CallbackQuery):
    await query.message.edit_text(
        (
            "<blockquote>🗂 <b>Yumeko Categories</b></blockquote>\n\n"
            "<i>❝ Choose the kind of thrill you want tonight, darling. ♡ ❞</i>\n\n"
            "Pick a category below."
        ),
        parse_mode=ParseMode.HTML,
        reply_markup=categories_buttons(),
        disable_web_page_preview=True,
    )
    await query.answer()

def game_info_caption(game_id: str):
    game = get_game(game_id)

    if not game:
        return "Game not found."

    return (
        f"<blockquote>{game['title']}</blockquote>\n\n"
        f"<i>❝ {game['caption']} ♡ ❞</i>\n\n"
        f"🎮 <b>Command:</b>\n"
        f"<code>{game['command']}</code>\n\n"
        f"📜 <b>Rules:</b>\n"
        f"{game['rules']}\n\n"
        f"🏆 <b>Rewards:</b>\n"
        f"{game['rewards']}"
    )


def game_info_buttons(category_id: str, page: int):
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅️ Back To Arcade", callback_data=f"yumeko_page_{category_id}_{page}")]]
    )


async def yumeko_cmd(client, message: Message):
    await message.reply_text(
        arcade_caption("all", 0),
        parse_mode=ParseMode.HTML,
        reply_markup=arcade_buttons("all", 0),
        disable_web_page_preview=True,
    )


async def yumeko_page_callback(client, query: CallbackQuery):
    data = query.data.replace("yumeko_page_", "", 1)

    try:
        category_id, page = data.rsplit("_", 1)
        page = int(page)
    except Exception:
        category_id = "all"
        page = 0

    await query.message.edit_text(
        arcade_caption(category_id, page),
        parse_mode=ParseMode.HTML,
        reply_markup=arcade_buttons(category_id, page),
        disable_web_page_preview=True,
    )
    await query.answer()


async def yumeko_game_info_callback(client, query: CallbackQuery):
    data = query.data.replace("ygameinfo_", "", 1)

    try:
        game_id, category_id, page = data.rsplit("_", 2)
        page = int(page)
    except Exception:
        await query.answer("Invalid game data.", show_alert=True)
        return

    await query.message.edit_text(
        game_info_caption(game_id),
        parse_mode=ParseMode.HTML,
        reply_markup=game_info_buttons(category_id, page),
        disable_web_page_preview=True,
    )
    await query.answer()


def register_group_arcade(app):
    app.add_handler(MessageHandler(yumeko_cmd, filters.command(["yumeko", "arcade"]) & filters.group), group=310)
    app.add_handler(CallbackQueryHandler(yumeko_page_callback, filters.regex("^yumeko_page_")), group=310)
    app.add_handler(CallbackQueryHandler(yumeko_game_info_callback, filters.regex("^ygameinfo_")), group=310)
    app.add_handler(
    CallbackQueryHandler(
        yumeko_categories_callback,
        filters.regex("^yumeko_categories$"),
    ),
    group=310,
    )