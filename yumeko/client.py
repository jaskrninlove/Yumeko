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

from pyrogram import Client
from yumeko.config import config

app = Client(
    name="Yumeko",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
    plugins=dict(root="yumeko.plugins"),
)