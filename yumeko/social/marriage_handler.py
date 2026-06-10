# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
#
#  Developer  : Jass
#  Project    : Yumeko Games Bot
#  Version    : 1.0.0
# ==========================================================

import random
import html

from pyrogram import filters
from pyrogram.enums import ChatType, ParseMode
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from yumeko.achievements.utils import check_marriage_achievement, check_love_achievement
from yumeko.database.users import add_user
from yumeko.social.marriage_db import (
    is_married,
    create_marriage,
    divorce_marriage,
    get_marriage,
    get_couple_rank,
    can_claim_love,
    claim_love,
    top_couples,
    get_daily_couple,
    set_daily_couple,
)
from yumeko.social.marriage_strings import (
    proposal_text,
    accepted_text,
    rejected_text,
    already_married_text,
    no_target_text,
    divorce_confirm_text,
    divorce_done_text,
    spouse_text,
    no_spouse_text,
    love_claimed_text,
    love_cooldown_text,
    top_couples_text,
    daily_couple_text,
    existing_daily_couple_text,
)


active_proposals = {}


def mention(user):
    name = html.escape(user.first_name or "Player")
    return f'<a href="tg://user?id={user.id}">{name}</a>'


def user_doc(user):
    return {"id": user.id, "name": user.first_name or "Unknown", "username": user.username}


def proposal_buttons(proposal_id: str):
    return InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("💖 Accept", callback_data=f"marry_accept:{proposal_id}"),
            InlineKeyboardButton("💔 Reject", callback_data=f"marry_reject:{proposal_id}"),
        ]]
    )


def divorce_buttons(user_id: int):
    return InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("💔 Confirm Divorce", callback_data=f"divorce_yes:{user_id}"),
            InlineKeyboardButton("❌ Cancel", callback_data=f"divorce_no:{user_id}"),
        ]]
    )


async def propose_cmd(client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        await message.reply_text("Marriage works only in groups.")
        return

    user = message.from_user
    target = message.reply_to_message.from_user if message.reply_to_message else None

    if not user:
        return

    if not target:
        await message.reply_text(no_target_text(message.command[0]), parse_mode=ParseMode.HTML)
        return

    if target.is_bot:
        await message.reply_text("Bots cannot be married, darling~")
        return

    if target.id == user.id:
        await message.reply_text("Marrying yourself? How lonely~")
        return

    chat_id = message.chat.id

    await add_user(user)
    await add_user(target)

    if await is_married(chat_id, user.id) or await is_married(chat_id, target.id):
        await message.reply_text(already_married_text(), parse_mode=ParseMode.HTML)
        return

    proposal_id = f"{chat_id}_{user.id}_{target.id}_{random.randint(1000, 9999)}"

    active_proposals[proposal_id] = {
        "chat_id": chat_id,
        "from": user_doc(user),
        "to": user_doc(target),
    }

    await message.reply_text(
        proposal_text(mention(user), mention(target)),
        parse_mode=ParseMode.HTML,
        reply_markup=proposal_buttons(proposal_id),
        reply_to_message_id=message.reply_to_message.id,
        disable_web_page_preview=True,
    )


async def accept_proposal(client, query: CallbackQuery):
    proposal_id = query.data.replace("marry_accept:", "", 1)
    data = active_proposals.get(proposal_id)

    if not data:
        await query.answer("This proposal expired, darling.", show_alert=True)
        return

    if query.from_user.id != data["to"]["id"]:
        await query.answer("Only the proposed person can accept.", show_alert=True)
        return

    chat_id = data["chat_id"]

    if await is_married(chat_id, data["from"]["id"]) or await is_married(chat_id, data["to"]["id"]):
        active_proposals.pop(proposal_id, None)
        await query.message.edit_text(already_married_text(), parse_mode=ParseMode.HTML)
        return

    await create_marriage(chat_id, data["from"], data["to"])
    await check_marriage_achievement(client, chat_id, data["from"]["id"])
    await check_marriage_achievement(client, chat_id, data["to"]["id"])
    active_proposals.pop(proposal_id, None)

    await query.message.edit_text(
        accepted_text(data["from"]["name"], data["to"]["name"]),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )
    await query.answer("Accepted!")


async def reject_proposal(client, query: CallbackQuery):
    proposal_id = query.data.replace("marry_reject:", "", 1)
    data = active_proposals.get(proposal_id)

    if not data:
        await query.answer("This proposal expired, darling.", show_alert=True)
        return

    if query.from_user.id != data["to"]["id"]:
        await query.answer("Only the proposed person can reject.", show_alert=True)
        return

    active_proposals.pop(proposal_id, None)

    await query.message.edit_text(
        rejected_text(data["to"]["name"]),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )
    await query.answer("Rejected.")


async def divorce_cmd(client, message: Message):
    user = message.from_user
    marriage = await get_marriage(message.chat.id, user.id)

    if not marriage:
        await message.reply_text(no_spouse_text(), parse_mode=ParseMode.HTML)
        return

    await message.reply_text(
        divorce_confirm_text(user.first_name or "Player"),
        parse_mode=ParseMode.HTML,
        reply_markup=divorce_buttons(user.id),
        reply_to_message_id=message.id,
    )


async def divorce_yes(client, query: CallbackQuery):
    user_id = int(query.data.replace("divorce_yes:", "", 1))

    if query.from_user.id != user_id:
        await query.answer("This divorce is not yours, darling.", show_alert=True)
        return

    marriage = await divorce_marriage(query.message.chat.id, user_id)

    if not marriage:
        await query.answer("Marriage not found.", show_alert=True)
        return

    await query.message.edit_text(
        divorce_done_text(marriage["user1"]["name"], marriage["user2"]["name"]),
        parse_mode=ParseMode.HTML,
    )
    await query.answer("Divorced.")


async def divorce_no(client, query: CallbackQuery):
    user_id = int(query.data.replace("divorce_no:", "", 1))

    if query.from_user.id != user_id:
        await query.answer("This button is not yours.", show_alert=True)
        return

    await query.message.edit_text(
        "<blockquote>💞 <b>Divorce Cancelled</b></blockquote>\n\n"
        "<i>❝ Love survives another round, darling. ♡ ❞</i>",
        parse_mode=ParseMode.HTML,
    )
    await query.answer("Cancelled.")


async def spouse_cmd(client, message: Message):
    user = message.from_user
    marriage = await get_marriage(message.chat.id, user.id)

    if not marriage:
        await message.reply_text(no_spouse_text(), parse_mode=ParseMode.HTML)
        return

    rank = await get_couple_rank(message.chat.id, marriage.get("love_points", 0))

    await message.reply_text(
        spouse_text(marriage, rank),
        parse_mode=ParseMode.HTML,
        reply_to_message_id=message.id,
        disable_web_page_preview=True,
    )


async def love_cmd(client, message: Message):
    user = message.from_user
    chat_id = message.chat.id

    can_claim, marriage, remaining = await can_claim_love(chat_id, user.id)

    if not marriage:
        await message.reply_text(no_spouse_text(), parse_mode=ParseMode.HTML)
        return

    if not can_claim:
        await message.reply_text(
            love_cooldown_text(remaining),
            parse_mode=ParseMode.HTML,
            reply_to_message_id=message.id,
        )
        return

    points = random.randint(15, 30)
    marriage = await claim_love(chat_id, user.id, points)
    await check_love_achievement(
    client,
    chat_id,
    user.id,
    marriage.get("love_points", 0),
)

    await message.reply_text(
        love_claimed_text(marriage, points),
        parse_mode=ParseMode.HTML,
        reply_to_message_id=message.id,
        disable_web_page_preview=True,
    )


async def top_couples_cmd(client, message: Message):
    couples = await top_couples(message.chat.id, limit=10)

    await message.reply_text(
        top_couples_text(couples),
        parse_mode=ParseMode.HTML,
        reply_to_message_id=message.id,
        disable_web_page_preview=True,
    )


async def couple_of_day_cmd(client, message: Message):
    chat_id = message.chat.id
    existing = await get_daily_couple(chat_id)

    if existing:
        await message.reply_text(
            existing_daily_couple_text(existing),
            parse_mode=ParseMode.HTML,
            reply_to_message_id=message.id,
        )
        return

    members = []

    async for member in client.get_chat_members(chat_id):
        if member.user and not member.user.is_bot:
            members.append(member.user)
        if len(members) >= 100:
            break

    if len(members) < 2:
        await message.reply_text("Not enough members found, darling~")
        return

    user1, user2 = random.sample(members, 2)
    doc = await set_daily_couple(chat_id, user_doc(user1), user_doc(user2))

    await message.reply_text(
        daily_couple_text(doc["user1"]["name"], doc["user2"]["name"]),
        parse_mode=ParseMode.HTML,
        reply_to_message_id=message.id,
        disable_web_page_preview=True,
    )


def register_marriage_handlers(app):
    app.add_handler(MessageHandler(propose_cmd, filters.command(["propose", "marry", "marriage"]) & filters.group), group=130)
    app.add_handler(MessageHandler(divorce_cmd, filters.command("divorce") & filters.group), group=130)
    app.add_handler(MessageHandler(spouse_cmd, filters.command(["spouse", "partner", "married", "coupleprofile"]) & filters.group), group=130)
    app.add_handler(MessageHandler(love_cmd, filters.command("love") & filters.group), group=130)
    app.add_handler(MessageHandler(top_couples_cmd, filters.command(["topcouples", "coupleboard"]) & filters.group), group=130)
    app.add_handler(MessageHandler(couple_of_day_cmd, filters.command(["coupleoftheday", "cotd", "couple"]) & filters.group), group=130)

    app.add_handler(CallbackQueryHandler(accept_proposal, filters.regex("^marry_accept:")), group=130)
    app.add_handler(CallbackQueryHandler(reject_proposal, filters.regex("^marry_reject:")), group=130)
    app.add_handler(CallbackQueryHandler(divorce_yes, filters.regex("^divorce_yes:")), group=130)
    app.add_handler(CallbackQueryHandler(divorce_no, filters.regex("^divorce_no:")), group=130)