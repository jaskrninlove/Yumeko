# ==========================================================
#  Yumeko Games Bot — Connect Four Buttons
#  Copyright (c) 2026 Jass
# ==========================================================

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def join_buttons():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🎮 Join Match", callback_data="c4_join"),
            ],
            [
                InlineKeyboardButton("▶️ Start", callback_data="c4_start"),
                InlineKeyboardButton("🛑 Cancel", callback_data="c4_cancel"),
            ],
        ]
    )


def column_buttons():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("1️⃣", callback_data="c4_col_0"),
                InlineKeyboardButton("2️⃣", callback_data="c4_col_1"),
                InlineKeyboardButton("3️⃣", callback_data="c4_col_2"),
                InlineKeyboardButton("4️⃣", callback_data="c4_col_3"),
            ],
            [
                InlineKeyboardButton("5️⃣", callback_data="c4_col_4"),
                InlineKeyboardButton("6️⃣", callback_data="c4_col_5"),
                InlineKeyboardButton("7️⃣", callback_data="c4_col_6"),
            ],
            [
                InlineKeyboardButton("🛑 End Match", callback_data="c4_end"),
            ],
        ]
    )


def after_game_buttons():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🔴🟡 Play Again", callback_data="c4_play_again"),
            ]
        ]
    )