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

import os
import asyncio

from yumeko.database.users import ensure_user_indexes

try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

from yumeko.client import app
from yumeko.core.database import ping_database
from yumeko.core.logger import startup, bot_started
from yumeko.core.notifier import send_log
from yumeko.locales import get_text

from yumeko.games.reaction.handler import register_reaction_handlers
from yumeko.games.typing_race.handler import register_typing_race_handlers
from yumeko.games.word_chain.handler import register_word_chain_handlers
from yumeko.games.bomb_party.handler import register_bomb_party_handlers
from yumeko.games.rps.handler import register_rps_handlers
from yumeko.games.toss.handler import register_toss_handlers
from yumeko.games.dice.handler import register_dice_handlers
from yumeko.games.slot.handler import register_slot_handlers
from yumeko.games.dart.handler import register_dart_handlers
from yumeko.games.basket.handler import register_basket_handlers
from yumeko.games.blackjack.handler import register_blackjack_handlers
from yumeko.social.marriage_handler import register_marriage_handlers
from yumeko.economy.handler import register_economy_handlers
from yumeko.shop.handler import register_shop_handlers
from yumeko.achievements.handler import register_achievement_handlers
from yumeko.achievements.db import ensure_achievement_indexes
from yumeko.pets.handler import register_pet_handlers
from yumeko.games.mafia.handler import register_mafia_handlers
from yumeko.leaderboards.handler import register_leaderboard_handlers
from yumeko.games.number_bomb.handler import register_number_bomb_handlers
from yumeko.games.fun.interaction_handler import register_interaction_handlers
from yumeko.games.party.handler import register_truth_dare_handlers
from yumeko.admin.owner_tools import register_owner_tools
from yumeko.plugins.group_arcade import register_group_arcade
from yumeko.games.hot_potato.handler import register_hot_potato_handlers
from yumeko.games.quiz_battle.handler import register_quiz_battle_handlers
from yumeko.plugins.fileid import *
from yumeko.games.tictactoe.handler import register_tictactoe_handlers
from yumeko.games.draw.draw_handler import register_draw_handlers
from yumeko.games.draw.webapp_handler import register_draw_webapp_handlers
from yumeko.games.connect4.handler import register_connect4_handlers
from yumeko.games.sports.handler import register_sports_handlers
from yumeko.games.racing.handler import register_racing_handlers
from yumeko.games.racing.handler import register_racing_handlers
register_racing_handlers(app)
from yumeko.games.poison_candy.handler import register_poison_candy_handlers
from yumeko.games.minesweeper.handler import register_minesweeper_handlers
from yumeko.games.mystery_box.handler import register_mystery_box_handlers
from yumeko.games.russian_roulette.handler import register_russian_roulette_handlers
from yumeko.games.chain_reaction.handler import register_chain_reaction_handlers
from yumeko.games.higher_lower.handler import register_higher_lower_handlers
from yumeko.games.safe_cracker.handler import register_safe_cracker_handlers
from yumeko.games.gomoku.handler import register_gomoku_handlers
from yumeko.games.battleship.handler import register_battleship_handlers
from yumeko.games.othello.handler import register_othello_handlers
from yumeko.games.dots_boxes.handler import register_dots_boxes_handlers

async def main():
    os.system("cls" if os.name == "nt" else "clear")

    startup()

    # Manual game handler registration
    register_reaction_handlers(app)
    register_typing_race_handlers(app)
    register_word_chain_handlers(app)
    register_bomb_party_handlers(app)
    register_rps_handlers(app)
    register_toss_handlers(app)
    register_dice_handlers(app)
    register_slot_handlers(app)
    register_dart_handlers(app)
    register_basket_handlers(app)
    register_blackjack_handlers(app)
    register_marriage_handlers(app)
    register_economy_handlers(app)
    register_shop_handlers(app)
    register_achievement_handlers(app)
    register_pet_handlers(app)
    register_mafia_handlers(app)
    register_leaderboard_handlers(app)
    register_number_bomb_handlers(app)
    register_interaction_handlers(app)
    register_truth_dare_handlers(app)
    register_owner_tools(app)
    register_group_arcade(app)
    register_hot_potato_handlers(app)
    register_quiz_battle_handlers(app)
    register_tictactoe_handlers(app)
    register_draw_handlers(app)
    db_status = await ping_database()
    await ensure_user_indexes()
    await ensure_achievement_indexes()
    register_draw_webapp_handlers(app)
    register_connect4_handlers(app)
    register_sports_handlers(app)
    register_racing_handlers(app)
    register_poison_candy_handlers(app)
    register_minesweeper_handlers(app)
    register_mystery_box_handlers(app)
    register_russian_roulette_handlers(app)
    register_chain_reaction_handlers(app)
    register_higher_lower_handlers(app)
    register_safe_cracker_handlers(app)
    register_gomoku_handlers(app)
    register_battleship_handlers(app)
    register_othello_handlers(app)
    register_dots_boxes_handlers(app)

    await app.start()

    me = await app.get_me()
    bot_started(me.username, me.id)

    await send_log(app, get_text("startup_log"))

    print(
        f"""
====================================================
                YUMEKO GAMES BOT
====================================================

Status      : Online
Database    : {"Connected" if db_status else "Failed"}
Bot         : @{me.username}

Developer   : Jass
Version     : 1.0.0

====================================================
"""
    )

    await asyncio.Event().wait()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())