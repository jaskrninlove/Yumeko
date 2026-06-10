# # ==========================================================
# #  Yumeko Games Bot
# #  Copyright (c) 2026 Jass
# #
# #  Developer  : Jass
# #  Project    : Yumeko Games Bot
# #  Version    : 1.0.0
# #
# #  GitHub     : Private
# #  License    : MIT License
# #
# #  This file is part of Yumeko Games Bot.
# #  Unauthorized removal of this notice is discouraged.
# #
# #  © 2026 Jass. All Rights Reserved.
# # ==========================================================

# from pyrogram import filters
# from pyrogram.types import Message, CallbackQuery

# from yumeko.client import app
# from yumeko.core.games_registry import get_category, get_game
# from yumeko.helpers.buttons import (
#     games_menu_buttons,
#     game_category_buttons,
#     game_info_buttons,
#     game_detail_buttons,
# )
# from yumeko.locales import get_text


# @app.on_message(filters.command("games"))
# async def games_cmd(_, message: Message):
#     await message.reply_text(
#         get_text("games_caption"),
#         reply_markup=games_menu_buttons(),
#         disable_web_page_preview=True,
#     )


# @app.on_callback_query(filters.regex("^gamecat_"))
# async def game_category_callback(_, query: CallbackQuery):
#     category_id = query.data.split("_", 1)[1]
#     category = get_category(category_id)

#     if not category:
#         await query.answer("Category not found.", show_alert=True)
#         return

#     await query.message.edit_text(
#         get_text(
#             "game_category_caption",
#             title=category["title"],
#             description=category["description"],
#         ),
#         reply_markup=game_category_buttons(category_id),
#         disable_web_page_preview=True,
#     )
#     await query.answer()


# @app.on_callback_query(filters.regex("^gameinfo_"))
# async def game_info_callback(_, query: CallbackQuery):
#     game_id = query.data.split("_", 1)[1]
#     game = get_game(game_id)

#     if not game:
#         await query.answer("Game not found.", show_alert=True)
#         return

#     await query.message.edit_text(
#         get_text(
#             "game_info_caption",
#             title=game["title"],
#             command=game["command"],
#             players=game["players"],
#             status=game["status"].replace("_", " ").title(),
#         ),
#         reply_markup=game_info_buttons(game_id, game["category"]),
#         disable_web_page_preview=True,
#     )
#     await query.answer()


# @app.on_callback_query(filters.regex("^gamehelp_"))
# async def game_help_callback(_, query: CallbackQuery):
#     game_id = query.data.split("_", 1)[1]
#     game = get_game(game_id)

#     if not game:
#         await query.answer("Game not found.", show_alert=True)
#         return

#     await query.message.edit_text(
#         get_text(game["help_key"]),
#         reply_markup=game_detail_buttons(game_id),
#         disable_web_page_preview=True,
#     )
#     await query.answer()


# @app.on_callback_query(filters.regex("^gamerules_"))
# async def game_rules_callback(_, query: CallbackQuery):
#     game_id = query.data.split("_", 1)[1]
#     game = get_game(game_id)

#     if not game:
#         await query.answer("Game not found.", show_alert=True)
#         return

#     await query.message.edit_text(
#         get_text(game["rules_key"]),
#         reply_markup=game_detail_buttons(game_id),
#         disable_web_page_preview=True,
#     )
#     await query.answer()


# @app.on_callback_query(filters.regex("^gamerewards_"))
# async def game_rewards_callback(_, query: CallbackQuery):
#     game_id = query.data.split("_", 1)[1]
#     game = get_game(game_id)

#     if not game:
#         await query.answer("Game not found.", show_alert=True)
#         return

#     await query.message.edit_text(
#         get_text(game["rewards_key"]),
#         reply_markup=game_detail_buttons(game_id),
#         disable_web_page_preview=True,
#     )
#     await query.answer()