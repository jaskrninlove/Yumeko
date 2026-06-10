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

from yumeko.config import config
from yumeko.core.logger import logger


async def send_log(client, text: str):
    if not config.LOGGER_CHAT_ID:
        return

    try:
        await client.send_message(
            chat_id=config.LOGGER_CHAT_ID,
            text=text,
            disable_web_page_preview=True,
        )
    except Exception as e:
        logger.error(f"Logger group error: {e}")