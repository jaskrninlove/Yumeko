from pyrogram import filters
from pyrogram.types import Message

from yumeko.client import app


@app.on_message(filters.command("fileid"))
async def fileid_cmd(_, message: Message):

    if not message.reply_to_message:
        return await message.reply_text(
            "Reply to a GIF, sticker, photo, video, animation or document."
        )

    msg = message.reply_to_message

    file_id = None

    if msg.animation:
        file_id = msg.animation.file_id

    elif msg.sticker:
        file_id = msg.sticker.file_id

    elif msg.photo:
        file_id = msg.photo.file_id

    elif msg.video:
        file_id = msg.video.file_id

    elif msg.document:
        file_id = msg.document.file_id

    elif msg.voice:
        file_id = msg.voice.file_id

    elif msg.video_note:
        file_id = msg.video_note.file_id

    if not file_id:
        return await message.reply_text(
            "Unsupported media type."
        )

    await message.reply_text(
        f"<blockquote><b>Telegram File ID</b></blockquote>\n\n"
        f"<code>{file_id}</code>",
        quote=True,
    )