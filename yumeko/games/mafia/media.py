# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
# ==========================================================

from pyrogram.enums import ParseMode


async def mafia_send(
    client,
    chat_id: int,
    text: str,
    gif: str | None = None,
    reply_markup=None,
):
    if gif:
        try:
            return await client.send_animation(
                chat_id,
                gif,
                caption=text,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup,
            )
        except Exception:
            pass

    return await client.send_message(
        chat_id,
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup,
        disable_web_page_preview=True,
    )