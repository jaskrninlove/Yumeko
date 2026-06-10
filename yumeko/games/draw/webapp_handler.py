# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
# ==========================================================

import base64
import json
from io import BytesIO

from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message


async def draw_webapp_data(client, message: Message):
    """
    Receives Telegram WebApp data from the canvas.

    Pyrogram versions may not include filters.web_app_data,
    so this handler listens to private messages and safely ignores
    anything that is not WebApp data.
    """

    web_app_data = getattr(message, "web_app_data", None)

    if not web_app_data:
        return

    try:
        raw_data = web_app_data.data
        data = json.loads(raw_data)

        image_data = data.get("image")
        chat_id = int(data.get("chat_id", 0))
        strokes = data.get("strokes", 0)
        colors = data.get("colors", 0)

        if not image_data or not chat_id:
            await message.reply_text("❌ Invalid drawing data received.")
            return

        if "," in image_data:
            image_data = image_data.split(",", 1)[1]

        image_bytes = base64.b64decode(image_data)

        photo = BytesIO(image_bytes)
        photo.name = "yumeko-drawing.jpg"

        await client.send_photo(
            chat_id,
            photo,
            caption=(
                "<blockquote>🎨 <b>Canvas Submitted</b></blockquote>\n\n"
                "The artist has submitted the drawing.\n"
                "Start guessing now, darling~\n\n"
                f"🖌 Strokes: <b>{strokes}</b>\n"
                f"🎨 Colors Used: <b>{colors}</b>"
            ),
            parse_mode=ParseMode.HTML,
        )

        await message.reply_text("✅ Drawing submitted to group.")

    except Exception as e:
        print(f"[DRAW WEBAPP ERROR] {e}")
        await message.reply_text(
            "❌ Failed to submit drawing. Please try again."
        )


def register_draw_webapp_handlers(app):
    app.add_handler(
        MessageHandler(
            draw_webapp_data,
            filters.private,
        ),
        group=270,
    )