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

from motor.motor_asyncio import AsyncIOMotorClient

from yumeko.config import config
from yumeko.core.logger import database_connected, database_failed


mongo = AsyncIOMotorClient(config.MONGO_URI)
db = mongo["YumekoGamesBot"]

users_col = db["users"]
groups_col = db["groups"]


async def ping_database() -> bool:
    try:
        await mongo.admin.command("ping")
        database_connected()
        return True
    except Exception as e:
        database_failed(e)
        return False