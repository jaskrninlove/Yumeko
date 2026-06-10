# ==========================================================
#  Yumeko Games Bot — Universal End Game Command
#  Copyright (c) 2026 Jass
# ==========================================================

from importlib import import_module

from pyrogram import filters
from pyrogram.enums import ChatType, ParseMode
from pyrogram.types import Message

from yumeko.client import app
from yumeko.core.game_manager import (
    is_game_running,
    get_running_game,
    force_unlock_game,
)
from yumeko.helpers.permissions import is_admin


GAME_MODULES = [
    ("Reaction Battle", "yumeko.games.reaction.game"),
    ("Typing Race", "yumeko.games.typing_race.game"),
    ("Word Chain", "yumeko.games.word_chain.game"),
    ("Bomb Party", "yumeko.games.bomb_party.game"),
    ("Quiz Battle", "yumeko.games.quiz_battle.game"),
    ("Hot Potato", "yumeko.games.hot_potato.game"),
    ("Draw & Guess", "yumeko.games.draw.game"),
    ("Fake Artist", "yumeko.games.fake_artist.game"),

    ("Connect Four", "yumeko.games.connect4.game"),
    ("Tic Tac Toe", "yumeko.games.tictactoe.game"),
    ("Chain Reaction", "yumeko.games.chain_reaction.game"),
    ("Gomoku", "yumeko.games.gomoku.game"),
    ("Battleship Royale", "yumeko.games.battleship.game"),

    ("Minesweeper", "yumeko.games.minesweeper.game"),
    ("Safe Cracker", "yumeko.games.safe_cracker.game"),
    ("Higher or Lower", "yumeko.games.higher_lower.game"),
    ("Poison Candy", "yumeko.games.poison_candy.game"),
    ("Mystery Box Royale", "yumeko.games.mystery_box.game"),
    ("Russian Roulette", "yumeko.games.russian_roulette.game"),

    ("Racing Duel", "yumeko.games.racing.game"),
    ("Sports Games", "yumeko.games.sports.game"),
]


async def _try_end_module(chat_id: int, module_path: str) -> bool:
    try:
        mod = import_module(module_path)
    except Exception:
        return False

    get_game = getattr(mod, "get_game", None)
    end_game = getattr(mod, "end_game", None)

    if not get_game or not end_game:
        return False

    try:
        game = get_game(chat_id)
    except Exception:
        game = None

    if not game:
        return False

    try:
        end_game(chat_id)
        return True
    except Exception:
        return False


async def clear_game_state(chat_id: int, game_name: str | None = None):
    stopped = []

    for title, module_path in GAME_MODULES:
        ok = await _try_end_module(chat_id, module_path)
        if ok:
            stopped.append(title)

    return stopped


@app.on_message(filters.command(["endgame", "stopgame", "cancelgame"]))
async def end_game_cmd(client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        await message.reply_text("This command can only be used in groups.")
        return

    chat_id = message.chat.id
    user = message.from_user

    if not user:
        return

    if not await is_admin(client, chat_id, user.id):
        await message.reply_text("Only group admins can end the current game.")
        return

    manager_game_name = get_running_game(chat_id) if is_game_running(chat_id) else None
    stopped = await clear_game_state(chat_id, manager_game_name)

    if is_game_running(chat_id):
        force_unlock_game(chat_id)

    if not stopped and not manager_game_name:
        await message.reply_text(
            "<blockquote>🎭 <b>No Active Game</b></blockquote>\n\n"
            "<i>❝ There is no game on the table right now, darling. ❞</i>",
            parse_mode=ParseMode.HTML,
        )
        return

    stopped_text = ", ".join(stopped) if stopped else manager_game_name

    await message.reply_text(
        "<blockquote>🛑 <b>Game Ended</b></blockquote>\n\n"
        "<i>❝ The thrill is over... for now. ❞</i>\n\n"
        f"Stopped game: <b>{stopped_text}</b>",
        parse_mode=ParseMode.HTML,
    )