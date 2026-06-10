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

import sys
import logging
from logging.handlers import RotatingFileHandler

# ----------------------------------------------------------
# Logging Configuration
# ----------------------------------------------------------

LOG_FORMAT = "[%(levelname)s] %(message)s"

file_handler = RotatingFileHandler(
    "yumeko.log",
    maxBytes=10_000_000,
    backupCount=5,
    encoding="utf-8",
)

console_handler = logging.StreamHandler(sys.stdout)

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        file_handler,
        console_handler,
    ],
)

# Silence noisy libraries
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("asyncio").setLevel(logging.ERROR)
logging.getLogger("motor").setLevel(logging.ERROR)
logging.getLogger("pymongo").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)

logger = logging.getLogger("Yumeko")


# ----------------------------------------------------------
# Helper Logging Functions
# ----------------------------------------------------------

def startup():
    logger.info("Starting Yumeko Games Bot...")


def database_connected():
    logger.info("MongoDB connected successfully.")


def database_failed(error):
    logger.error(f"MongoDB connection failed: {error}")


def bot_started(username, user_id):
    logger.info(f"Bot started as @{username} [{user_id}]")


def new_user(name, user_id):
    logger.info(f"New user: {name} [{user_id}]")


def user_opened(name, user_id):
    logger.info(f"User opened bot: {name} [{user_id}]")


def group_added(title, chat_id):
    logger.info(f"Added to group: {title} [{chat_id}]")


def group_removed(title, chat_id):
    logger.info(f"Removed from group: {title} [{chat_id}]")


def game_started(game_name, chat_id):
    logger.info(f"Game started: {game_name} [{chat_id}]")


def game_finished(game_name, winner):
    logger.info(f"Game finished: {game_name} | Winner: {winner}")


def broadcast_sent(total):
    logger.info(f"Broadcast sent to {total} users")


def error(error):
    logger.error(str(error))