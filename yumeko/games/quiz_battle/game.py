# ==========================================================
#  Yumeko Games Bot — Quiz Battle Game Logic
#  Copyright (c) 2026 Jass  |  Version 2.0.0
# ==========================================================

import asyncio
import random
import time
from datetime import datetime

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from yumeko.database.users import add_win, add_loss
from yumeko.database.groups import add_group_game, record_game_result
from yumeko.games.quiz_battle import strings as S

REWARD_COINS  = 60
REWARD_XP     = 30
LOSER_XP      = 10
MIN_PLAYERS   = 2
MAX_PLAYERS   = 20
JOIN_TIMEOUT  = 60
TOTAL_ROUNDS  = 10
ROUND_TIMEOUT = 20
SPEED_BONUS_S = 5
POINTS_FIRST  = 3
POINTS_SECOND = 1
POINTS_WRONG  = -1

active_games: dict[int, dict] = {}

# ── Question Bank ─────────────────────────────────────────
# Format: (question, [options], correct_index, category)

QUESTION_BANK = [
    ("What is the capital of Japan?",
     ["Beijing", "Seoul", "Tokyo", "Bangkok"], 2, "🌍 Geography"),
    ("How many sides does a hexagon have?",
     ["5", "6", "7", "8"], 1, "📐 Math"),
    ("What gas do plants absorb during photosynthesis?",
     ["Oxygen", "Nitrogen", "Carbon Dioxide", "Hydrogen"], 2, "🔬 Science"),
    ("Which planet is known as the Red Planet?",
     ["Venus", "Mars", "Jupiter", "Saturn"], 1, "🌌 Space"),
    ("What is the chemical symbol for Gold?",
     ["Go", "Gd", "Au", "Ag"], 2, "⚗️ Chemistry"),
    ("Who painted the Mona Lisa?",
     ["Van Gogh", "Picasso", "Da Vinci", "Rembrandt"], 2, "🎨 Art"),
    ("What is the fastest land animal?",
     ["Lion", "Cheetah", "Horse", "Falcon"], 1, "🐾 Animals"),
    ("How many bones are in the adult human body?",
     ["196", "206", "216", "226"], 1, "🫀 Biology"),
    ("What year did World War II end?",
     ["1943", "1944", "1945", "1946"], 2, "📜 History"),
    ("Which ocean is the largest?",
     ["Atlantic", "Indian", "Arctic", "Pacific"], 3, "🌊 Geography"),
    ("What is the square root of 144?",
     ["10", "11", "12", "13"], 2, "📐 Math"),
    ("Which element has atomic number 1?",
     ["Helium", "Hydrogen", "Lithium", "Carbon"], 1, "⚗️ Chemistry"),
    ("What is the longest river in the world?",
     ["Amazon", "Mississippi", "Yangtze", "Nile"], 3, "🌍 Geography"),
    ("How many continents are there?",
     ["5", "6", "7", "8"], 2, "🌍 Geography"),
    ("What language has the most native speakers?",
     ["English", "Spanish", "Mandarin", "Hindi"], 2, "🗣️ Language"),
    ("What is 15% of 200?",
     ["25", "30", "35", "40"], 1, "📐 Math"),
    ("Which planet has the most moons?",
     ["Jupiter", "Saturn", "Uranus", "Neptune"], 1, "🌌 Space"),
    ("What is the hardest natural substance?",
     ["Gold", "Iron", "Diamond", "Quartz"], 2, "💎 Science"),
    ("Who wrote Romeo and Juliet?",
     ["Dickens", "Shakespeare", "Tolkien", "Homer"], 1, "📚 Literature"),
    ("What is the speed of light (approx)?",
     ["200,000 km/s", "300,000 km/s", "400,000 km/s", "500,000 km/s"], 1, "🔬 Physics"),
    ("Which country invented pizza?",
     ["France", "Greece", "Italy", "Spain"], 2, "🍕 Food"),
    ("What does CPU stand for?",
     ["Central Power Unit", "Central Processing Unit", "Computer Processing Unit", "Core Power Unit"], 1, "💻 Tech"),
    ("What is the largest mammal?",
     ["Elephant", "Giraffe", "Blue Whale", "Polar Bear"], 2, "🐋 Animals"),
    ("How many players are in a soccer team?",
     ["9", "10", "11", "12"], 2, "⚽ Sports"),
    ("What is the boiling point of water in Celsius?",
     ["90°C", "95°C", "100°C", "105°C"], 2, "🔬 Science"),
    ("Which country is the largest by area?",
     ["China", "USA", "Canada", "Russia"], 3, "🌍 Geography"),
    ("What is 8 × 9?",
     ["63", "72", "81", "64"], 1, "📐 Math"),
    ("Which instrument has 88 keys?",
     ["Guitar", "Violin", "Piano", "Harp"], 2, "🎵 Music"),
    ("What year did the Titanic sink?",
     ["1910", "1911", "1912", "1913"], 2, "📜 History"),
    ("What is the powerhouse of the cell?",
     ["Nucleus", "Ribosome", "Mitochondria", "Golgi body"], 2, "🔬 Biology"),
    ("Which country has the most pyramids?",
     ["Egypt", "Mexico", "Sudan", "Peru"], 2, "📜 History"),
    ("What does HTML stand for?",
     ["Hyper Text Markup Language", "High Text Machine Language",
      "Hyper Transfer Markup Logic", "Home Tool Markup Language"], 0, "💻 Tech"),
    ("How many strings does a standard guitar have?",
     ["4", "5", "6", "7"], 2, "🎵 Music"),
    ("What is the currency of Japan?",
     ["Won", "Yuan", "Yen", "Ringgit"], 2, "💰 Economy"),
    ("Who developed the theory of relativity?",
     ["Newton", "Edison", "Einstein", "Tesla"], 2, "🔬 Science"),
    ("What is the tallest mountain in the world?",
     ["K2", "Kangchenjunga", "Everest", "Lhotse"], 2, "🏔️ Geography"),
    ("Which vitamin does sunlight provide?",
     ["Vitamin A", "Vitamin C", "Vitamin D", "Vitamin E"], 2, "🫀 Health"),
    ("What is the smallest country in the world?",
     ["Monaco", "Vatican City", "San Marino", "Liechtenstein"], 1, "🌍 Geography"),
    ("How many colors are in a rainbow?",
     ["5", "6", "7", "8"], 2, "🌈 Nature"),
    ("What is 2 to the power of 10?",
     ["512", "1024", "2048", "256"], 1, "📐 Math"),
    ("Which gas makes up most of Earth's atmosphere?",
     ["Oxygen", "Carbon Dioxide", "Nitrogen", "Argon"], 2, "🌎 Science"),
    ("What is the chemical formula for water?",
     ["HO2", "H2O", "H2O2", "OH"], 1, "⚗️ Chemistry"),
    ("Which country won the first FIFA World Cup?",
     ["Brazil", "Argentina", "Uruguay", "Italy"], 2, "⚽ Sports"),
    ("What organ filters blood in the human body?",
     ["Liver", "Heart", "Kidney", "Lungs"], 2, "🫀 Biology"),
    ("How many days are in a leap year?",
     ["364", "365", "366", "367"], 2, "📅 General"),
    ("Who was the first person on the moon?",
     ["Buzz Aldrin", "Yuri Gagarin", "Neil Armstrong", "John Glenn"], 2, "🌌 Space"),
    ("What is the largest organ in the human body?",
     ["Heart", "Liver", "Brain", "Skin"], 3, "🫀 Biology"),
    ("Which metal is liquid at room temperature?",
     ["Lead", "Mercury", "Gallium", "Cesium"], 1, "⚗️ Chemistry"),
    ("What is the most spoken language in the world?",
     ["English", "Spanish", "Mandarin Chinese", "Hindi"], 2, "🗣️ Language"),
    ("What does RAM stand for?",
     ["Random Access Memory", "Read Access Module", "Runtime Active Memory", "Random App Module"], 0, "💻 Tech"),
]


# ── State ─────────────────────────────────────────────────

def create_game(chat_id, host_id, host_name):
    active_games[chat_id] = {
        "host_id":    host_id,
        "host_name":  host_name,
        "players":    {},
        "scores":     {},
        "status":     "joining",
        "round":      0,
        "questions":  [],
        "round_open": False,
        "round_answered": set(),
        "round_start_time": None,
        "started_at": datetime.utcnow(),
    }

def get_game(chat_id): return active_games.get(chat_id)
def end_game(chat_id): active_games.pop(chat_id, None)

def join_game(chat_id, user):
    game = get_game(chat_id)
    if not game:                            return False, "no_game"
    if game["status"] != "joining":         return False, "started"
    if len(game["players"]) >= MAX_PLAYERS: return False, "full"
    if user.id in game["players"]:          return False, "joined"
    game["players"][user.id] = {"name": user.first_name or "Unknown"}
    game["scores"][user.id]  = 0
    return True, "ok"

def format_players(game):
    lines = []
    for uid, p in game["players"].items():
        pts = game["scores"].get(uid, 0)
        lines.append(f"  🃏 <b>{p['name']}</b>  —  {pts} pts")
    return "\n".join(lines) if lines else "  <i>No players~</i>"

def score_board(game):
    sorted_s = sorted(game["scores"].items(), key=lambda x: x[1], reverse=True)
    medals   = ["🥇","🥈","🥉"] + ["🔹"] * 20
    lines    = []
    for i, (uid, pts) in enumerate(sorted_s):
        name = game["players"].get(uid, {}).get("name", "?")
        lines.append(f"  {medals[i]} <b>{name}</b>  —  {pts} pts")
    return "\n".join(lines)

def answer_buttons(options: list, game_id_prefix: str = "qz") -> InlineKeyboardMarkup:
    labels = ["🅰️","🅱️","🇨","🇩"]
    rows   = []
    for i, opt in enumerate(options):
        rows.append([InlineKeyboardButton(
            f"{labels[i]}  {opt}",
            callback_data=f"{game_id_prefix}_ans_{i}",
        )])
    return InlineKeyboardMarkup(rows)

def join_buttons() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🧠 Join Quiz",  callback_data="qz_join"),
            InlineKeyboardButton("🚀 Start!",     callback_data="qz_start"),
        ],
        [InlineKeyboardButton("❌ Cancel",        callback_data="qz_cancel")],
    ])


# ── Core round ────────────────────────────────────────────

async def run_round(client, message, chat_id: int, round_num: int):
    game = get_game(chat_id)
    if not game: return

    q_data  = game["questions"][round_num - 1]
    q_text  = q_data[0]
    options = q_data[1]
    correct = q_data[2]
    cat     = q_data[3]

    game["round_open"]        = True
    game["round_answered"]    = set()
    game["round_correct_idx"] = correct
    game["round_start_time"]  = time.time()
    game["first_correct"]     = None

    q_msg = await message.reply_text(
        S.question_text(round_num, TOTAL_ROUNDS, cat, q_text, options, ROUND_TIMEOUT),
        reply_markup=answer_buttons(options),
    )

    # Wait for round timeout
    await asyncio.sleep(ROUND_TIMEOUT)

    game = get_game(chat_id)
    if not game: return

    game["round_open"] = False

    correct_answer = options[correct]
    if not game.get("first_correct"):
        try:
            await q_msg.edit_text(
                q_msg.text + "\n\n" + S.round_timeout(correct_answer),
                reply_markup=None,
            )
        except: pass
    else:
        try:
            await q_msg.edit_reply_markup(None)
        except: pass

    await asyncio.sleep(2)

    # Show scoreboard
    await message.reply_text(
        S.round_scoreboard(
            {game["players"][uid]["name"]: pts for uid, pts in game["scores"].items()},
            round_num, TOTAL_ROUNDS,
        )
    )
    await asyncio.sleep(3)


async def run_game(client, message, chat_id: int):
    game = get_game(chat_id)
    if not game: return

    # Pick random questions
    pool              = random.sample(QUESTION_BANK, min(TOTAL_ROUNDS, len(QUESTION_BANK)))
    game["questions"] = pool
    game["status"]    = "running"

    for round_num in range(1, TOTAL_ROUNDS + 1):
        game = get_game(chat_id)
        if not game or game["status"] != "running": return
        game["round"] = round_num
        await run_round(client, message, chat_id, round_num)

    await finish_game(client, message, chat_id)


async def finish_game(client, message, chat_id: int):
    game = get_game(chat_id)
    if not game: return

    if not game["scores"]:
        await message.reply_text("😴 <i>No answers recorded~  No winner~  ♡</i>")
        end_game(chat_id); return

    winner_id   = max(game["scores"], key=lambda x: game["scores"][x])
    winner_name = game["players"][winner_id]["name"]
    name_scores = {game["players"][uid]["name"]: pts
                   for uid, pts in game["scores"].items()}

    await add_win(winner_id, coins=REWARD_COINS, xp=REWARD_XP)
    for uid in game["players"]:
        if uid != winner_id:
            await add_loss(uid, xp=LOSER_XP)

    await add_group_game(chat_id, game_type="quiz_battle")
    await record_game_result(chat_id, "quiz_battle", winner_id, winner_name,
                             len(game["players"]))

    await message.reply_text(
        S.victory_text(winner_name, name_scores, TOTAL_ROUNDS, REWARD_COINS, REWARD_XP)
    )
    end_game(chat_id)