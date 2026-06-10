# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass  |  Version 2.0.0
# ==========================================================

import random

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from yumeko.config import config
from yumeko.core.games_registry import (
    get_all_categories,
    get_game,
    paginated_games,
    GAMES_PER_PAGE,
)


# ── Yumeko flavor lines (used across captions) ────────────────────────────────

_ARCADE_FLAVORS = [
    "Every command is a gamble. Every reward has a price. ♡",
    "Welcome to my table, darling. Choose carefully.",
    "Ahahaha~ So many ways to lose yourself here. ♡",
    "The games never stop. Neither does the thrill. ♡",
    "Step in. The stage is already set for you.",
]

_INFO_FLAVORS = [
    "Tap below to reveal how this little gamble works. ♡",
    "Every game has a soul. Let me show you this one.",
    "Curious~ How delightful. Read on, darling.",
    "The rules are simple. The risk is not. ♡",
    "Know the game before you play it. Or don't. ♡",
]

_RULES_FLAVORS = [
    "Rules make the gamble sweeter, darling. ♡",
    "Even chaos has structure. Learn it.",
    "The rules exist to be understood — and sometimes bent. ♡",
    "Read carefully. The difference between winning and losing is right here.",
]

_REWARDS_FLAVORS = [
    "Win beautifully, lose dramatically. Either way, play. ♡",
    "The reward is real. The risk is realer. ♡",
    "Ahahaha~ This is what you're fighting for. ♡",
    "Every coin earned at this table means something.",
]

_HOW_FLAVORS = [
    "Now go on, darling. The table is waiting. ♡",
    "You know what to do. Go play. ♡",
    "Ahahaha~ Don't keep me waiting. ♡",
    "The command is simple. The excitement is not. ♡",
]


# ── Core keyboard builders ────────────────────────────────────────────────────

def start_buttons() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("♞ Yumeko Gaming Hub ♞", callback_data="games_page_all_0")],
        [
            InlineKeyboardButton("𓆰 Help",   callback_data="help_menu"),
            InlineKeyboardButton("Owner ♛",  callback_data="owner_menu"),
        ],
        [
            InlineKeyboardButton("☊ Support",  url=config.SUPPORT_GROUP),
            InlineKeyboardButton("Updates ❆",  url=config.UPDATE_CHANNEL),
        ],
        [
            InlineKeyboardButton(
                "🃟 Add Me To Group 🃟",
                url=f"https://t.me/{config.BOT_USERNAME}?startgroup=true",
            )
        ],
    ])


def group_start_buttons() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("♞ Open Games ♞", callback_data="games_page_all_0")],
    ])


def group_added_buttons() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("♞ Explore Yumeko Games ♞", callback_data="games_page_all_0")],
    ])


def back_home_buttons(back_callback: str = "start_home") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⬿ Back",  callback_data=back_callback),
            InlineKeyboardButton("❉ Home",  callback_data="start_home"),
        ],
    ])


def games_menu_buttons() -> InlineKeyboardMarkup:
    rows = []
    temp = []

    for cat_id, cat in get_all_categories().items():
        temp.append(InlineKeyboardButton(
            cat["title"],
            callback_data=f"games_page_{cat_id}_0",
        ))
        if len(temp) == 2:
            rows.append(temp)
            temp = []

    if temp:
        rows.append(temp)

    rows.append([InlineKeyboardButton("❉ Home", callback_data="start_home")])
    return InlineKeyboardMarkup(rows)


def games_page_buttons(category_id: str = "all", page: int = 0) -> InlineKeyboardMarkup:
    rows = []
    games, total = paginated_games(category_id, page)
    temp = []

    for game_id, game in games:
        temp.append(InlineKeyboardButton(
            game["title"],
            callback_data=f"gameinfo_{game_id}",
        ))
        if len(temp) == 2:
            rows.append(temp)
            temp = []

    if temp:
        rows.append(temp)

    # Pagination row
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(
            "⬿ Prev",
            callback_data=f"games_page_{category_id}_{page - 1}",
        ))
    if (page + 1) * GAMES_PER_PAGE < total:
        nav.append(InlineKeyboardButton(
            "Next ⤳",
            callback_data=f"games_page_{category_id}_{page + 1}",
        ))
    if nav:
        rows.append(nav)

    rows.append([
        InlineKeyboardButton("♕ Categories", callback_data="games_menu"),
        InlineKeyboardButton("Home ❉ ",       callback_data="start_home"),
    ])
    return InlineKeyboardMarkup(rows)


def game_info_buttons(game_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🂡 Play Command",  callback_data=f"gamecmd_{game_id}"),
            InlineKeyboardButton("How To Play ♞",   callback_data=f"gamehelp_{game_id}"),
        ],
        [
            InlineKeyboardButton("♛ Rules",         callback_data=f"gamerules_{game_id}"),
            InlineKeyboardButton("Rewards ★",       callback_data=f"gamerewards_{game_id}"),
        ],
        [
            InlineKeyboardButton("⬿ Back",          callback_data="games_page_all_0"),
            InlineKeyboardButton("Home ❆",           callback_data="start_home"),
        ],
    ])


def game_detail_buttons(game_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⬿ Back",  callback_data=f"gameinfo_{game_id}"),
            InlineKeyboardButton("Home ❆",  callback_data="start_home"),
        ],
    ])


# Alias kept for backward compat
def game_category_buttons(category_id: str) -> InlineKeyboardMarkup:
    return games_page_buttons(category_id, 0)

def game_info_buttons_old(game_id: str, category_id: str = "all") -> InlineKeyboardMarkup:
    return game_info_buttons(game_id)


# ── Caption builders ──────────────────────────────────────────────────────────

def games_page_caption(category_id: str = "all", page: int = 0) -> str:
    category = get_all_categories().get(category_id, {"title": "🎮 Yumeko Arcade"})
    games, total = paginated_games(category_id, page)
    total_pages  = max(1, (total + GAMES_PER_PAGE - 1) // GAMES_PER_PAGE)

    return (
        f"<blockquote>{category['title']}</blockquote>\n\n"
        f"<i>❝ {random.choice(_ARCADE_FLAVORS)} ❞</i>\n\n"
        f"🎲 Entries: <b>{total}</b>  ·  "
        f"📄 Page: <b>{page + 1} / {total_pages}</b>\n\n"
        f"<i>Choose your table below, darling.</i>"
    )


def game_info_caption(game_id: str) -> str:
    game = get_game(game_id)
    if not game:
        return "<i>❝ This game doesn't exist~  Or maybe it does and you're not ready for it. ❞</i>"

    return (
        f"<blockquote>{game['title']}</blockquote>\n\n"
        f"<i>❝ {game['caption']} ♡ ❞</i>\n\n"
        f"🎮 Command:  <code>{game['command']}</code>\n\n"
        f"<i>{random.choice(_INFO_FLAVORS)}</i>"
    )


def game_command_caption(game_id: str) -> str:
    game = get_game(game_id)
    if not game:
        return "<i>❝ Game not found. ❞</i>"

    return (
        f"<blockquote>🂡 <b>Play Command</b></blockquote>\n\n"
        f"<b>{game['title']}</b>\n\n"
        f"Use this command to start:\n\n"
        f"<code>{game['command']}</code>\n\n"
        f"<i>❝ {random.choice(_HOW_FLAVORS)} ❞</i>"
    )


def game_help_caption(game_id: str) -> str:
    game = get_game(game_id)
    if not game:
        return "<i>❝ Game not found. ❞</i>"

    return (
        f"<blockquote>♞ <b>How To Play</b></blockquote>\n\n"
        f"<b>{game['title']}</b>\n\n"
        f"<i>❝ {game['caption']} ❞</i>\n\n"
        f"Start with:\n<code>{game['command']}</code>\n\n"
        f"<i>{random.choice(_HOW_FLAVORS)}</i>"
    )


def game_rules_caption(game_id: str) -> str:
    game = get_game(game_id)
    if not game:
        return "<i>❝ Game not found. ❞</i>"

    return (
        f"<blockquote>♛ <b>Rules</b></blockquote>\n\n"
        f"<b>{game['title']}</b>\n\n"
        f"{game['rules']}\n\n"
        f"<i>❝ {random.choice(_RULES_FLAVORS)} ❞</i>"
    )


def game_rewards_caption(game_id: str) -> str:
    game = get_game(game_id)
    if not game:
        return "<i>❝ Game not found. ❞</i>"

    return (
        f"<blockquote>★ <b>Rewards</b></blockquote>\n\n"
        f"<b>{game['title']}</b>\n\n"
        f"{game['rewards']}\n\n"
        f"<i>❝ {random.choice(_REWARDS_FLAVORS)} ❞</i>"
    )