# ==========================================================
#  Yumeko Games Bot — Yumeko Sketch
#  Copyright (c) 2026 Jass
# ==========================================================

import random
from datetime import datetime

# ── Active games ──────────────────────────────────────────
active_draw_games: dict = {}   # chat_id → game dict

# ── Constants ─────────────────────────────────────────────
MIN_PLAYERS   = 2
MAX_PLAYERS   = 12
JOIN_TIME     = 45
DRAW_TIME     = 120    # seconds for the drawer
GUESS_TIME    = 120    # same window — guessing happens while drawer is drawing
ROUNDS        = 3

POINTS_FAST   = 300   # guessed in first 20s after image posted
POINTS_MID    = 200   # 21–50s
POINTS_SLOW   = 100   # 51s+
POINTS_DRAWER = 40    # per correct guesser (drawer earns this)
POINTS_BONUS  = 50    # bonus if everyone guesses

WIN_COINS     = 250
WIN_XP        = 120
LOSE_XP       = 25
BONUS_COINS   = 50

# ── Word Bank ─────────────────────────────────────────────
WORDS = {
    "easy": [
        "cat","dog","house","tree","sun","moon","fish","bird","car","ball",
        "hat","cake","book","star","flower","eye","hand","fire","rain","cloud",
        "apple","heart","key","door","bed","chair","phone","shoe","cup","pizza",
        "banana","sword","crown","boat","bell","drum","clock","lamp","flag","leaf",
    ],
    "medium": [
        "umbrella","rainbow","ladder","bridge","guitar","castle","dragon",
        "butterfly","astronaut","lighthouse","volcano","tornado","submarine",
        "treasure","cactus","compass","lantern","anchor","telescope","crown",
        "potion","scroll","mask","candle","hourglass","map","shield","bow",
        "crystal","ghost","wizard","mermaid","tornado","hurricane","avalanche",
        "pyramid","sphinx","snowflake","aurora","hammock",
    ],
    "hard": [
        "nostalgia","democracy","philosophy","nightmare","jealousy",
        "meditation","revolution","conspiracy","paradox","infinity",
        "gravity","evolution","illusion","dimension","soulmate",
        "labyrinth","forbidden","prophecy","betrayal","destiny",
        "quarantine","ecosystem","renaissance","apocalypse","odyssey",
    ],
    "yumeko": [
        "gamble","poker face","risky bet","loaded dice","card shark",
        "bluff master","royal flush","double or nothing","house of cards",
        "wild card","ace up sleeve","casino night","dead mans hand",
        "all in","bad hand","high roller","shuffle","jackpot",
    ],
}

ALL_WORDS = (
    WORDS["easy"] * 3
    + WORDS["medium"] * 2
    + WORDS["hard"]
    + WORDS["yumeko"] * 2
)


def pick_word_choices(n: int = 3) -> list[str]:
    pool = list(set(ALL_WORDS))
    random.shuffle(pool)
    return pool[:n]


def masked_word(word: str) -> str:
    return " ".join("_" if c.isalpha() else c for c in word)


def word_with_hint(word: str, reveal_count: int) -> str:
    """Reveal `reveal_count` random letters."""
    chars = list(word)
    letter_indices = [i for i, c in enumerate(chars) if c.isalpha()]
    random.shuffle(letter_indices)
    revealed = set(letter_indices[:reveal_count])
    result = []
    for i, c in enumerate(chars):
        if c == " ":
            result.append("  ")
        elif i in revealed:
            result.append(c.upper())
        else:
            result.append("_")
    return " ".join(result)


# ── Lifecycle ─────────────────────────────────────────────

def create_draw_game(chat_id: int, host_id: int, host_name: str) -> dict:
    game = {
        "chat_id":      chat_id,
        "host_id":      host_id,
        "host_name":    host_name,
        "status":       "joining",    # joining→word_pick→drawing→guessing→ended

        "players":      {},           # uid → player dict
        "order":        [],           # uid turn order
        "round":        0,
        "turn_index":   0,

        "current_drawer":  None,
        "current_word":    None,
        "word_choices":    [],
        "hint_level":      0,

        "guessed":      {},           # uid → elapsed seconds
        "turn_start":   None,
        "drawing_msg_id":  None,
        "group_msg_id":    None,      # the pinned/updating guess msg

        "lobby_msg_id": None,
        "created_at":   datetime.utcnow(),
    }
    active_draw_games[chat_id] = game
    return game


def get_draw_game(chat_id: int):
    return active_draw_games.get(chat_id)


def end_draw_game(chat_id: int):
    active_draw_games.pop(chat_id, None)


def set_lobby_msg(chat_id: int, msg_id: int):
    g = get_draw_game(chat_id)
    if g:
        g["lobby_msg_id"] = msg_id


# ── Players ───────────────────────────────────────────────

def join_draw_game(chat_id: int, user) -> tuple[bool, str]:
    g = get_draw_game(chat_id)
    if not g:                          return False, "no_game"
    if g["status"] != "joining":       return False, "started"
    if user.id in g["players"]:        return False, "joined"
    if len(g["players"]) >= MAX_PLAYERS: return False, "full"

    g["players"][user.id] = {
        "id":              user.id,
        "name":            user.first_name or "Unknown",
        "username":        user.username,
        "score":           0,
        "rounds_drawn":    0,
        "correct_guesses": 0,
        "guessed_this_round": False,
        "afk_warnings":    0,
    }
    return True, "ok"


def get_player(game: dict, uid: int):
    return game["players"].get(uid)


def format_players_list(game: dict) -> str:
    if not game["players"]:
        return "No players yet."
    lines = []
    for i, p in enumerate(game["players"].values(), 1):
        uid = p["id"]
        lines.append(f'{i}. <a href="tg://user?id={uid}">{p["name"]}</a>')
    return "\n".join(lines)


# ── Turn management ───────────────────────────────────────

def start_game(chat_id: int) -> dict | None:
    g = get_draw_game(chat_id)
    if not g:
        return None
    ids = list(g["players"].keys())
    random.shuffle(ids)
    g["order"]      = ids
    g["round"]      = 1
    g["turn_index"] = 0
    g["status"]     = "word_pick"
    _assign_drawer(g)
    return g


def _assign_drawer(game: dict):
    order  = game["order"]
    idx    = game["turn_index"] % len(order)
    uid    = order[idx]
    game["current_drawer"]  = uid
    game["current_word"]    = None
    game["word_choices"]    = pick_word_choices(3)
    game["guessed"]         = {}
    game["hint_level"]      = 0
    game["turn_start"]      = None
    game["drawing_msg_id"]  = None
    game["group_msg_id"]    = None
    game["status"]          = "word_pick"

    for p in game["players"].values():
        p["guessed_this_round"] = False


def pick_word(chat_id: int, uid: int, word: str) -> tuple[bool, str]:
    g = get_draw_game(chat_id)
    if not g:                          return False, "no_game"
    if g["current_drawer"] != uid:     return False, "not_drawer"
    if g["status"] != "word_pick":     return False, "wrong_phase"
    g["current_word"] = word.lower()
    g["status"]       = "drawing"
    return True, "ok"


def submit_drawing(chat_id: int, uid: int) -> tuple[bool, str]:
    g = get_draw_game(chat_id)
    if not g:                          return False, "no_game"
    if g["current_drawer"] != uid:     return False, "not_drawer"
    if g["status"] != "drawing":       return False, "wrong_phase"
    g["status"]     = "guessing"
    g["turn_start"] = datetime.utcnow()
    return True, "ok"


def process_guess(chat_id: int, uid: int, text: str) -> tuple[str, int]:
    """
    Returns (code, points):
    code: correct | close | wrong | already | drawer | not_active
    """
    g = get_draw_game(chat_id)
    if not g or g["status"] != "guessing":  return "not_active", 0
    if uid == g["current_drawer"]:           return "drawer", 0
    if uid in g["guessed"]:                  return "already", 0
    if uid not in g["players"]:              return "wrong", 0

    word  = g["current_word"] or ""
    guess = text.strip().lower()

    if guess == word:
        elapsed = (datetime.utcnow() - g["turn_start"]).total_seconds()
        pts = POINTS_FAST if elapsed<=20 else (POINTS_MID if elapsed<=50 else POINTS_SLOW)

        g["guessed"][uid]  = elapsed
        g["players"][uid]["score"]           += pts
        g["players"][uid]["correct_guesses"] += 1
        g["players"][uid]["guessed_this_round"] = True

        # Drawer earns points
        di = g["current_drawer"]
        if di in g["players"]:
            g["players"][di]["score"] += POINTS_DRAWER

        return "correct", pts

    if _is_close(guess, word):
        return "close", 0

    return "wrong", 0


def _is_close(a: str, b: str) -> bool:
    if abs(len(a)-len(b)) > 1:
        return False
    if len(a) == len(b):
        return sum(x!=y for x,y in zip(a,b)) == 1
    short, long_ = (a,b) if len(a)<len(b) else (b,a)
    i=j=diffs=0
    while i<len(short) and j<len(long_):
        if short[i]!=long_[j]: diffs+=1; j+=1
        else: i+=1; j+=1
    return diffs<=1


def all_guessed(game: dict) -> bool:
    guessers = [u for u in game["players"] if u!=game["current_drawer"]]
    return len(guessers)>0 and all(u in game["guessed"] for u in guessers)


def advance_turn(chat_id: int) -> dict:
    g = get_draw_game(chat_id)
    if not g:
        return {"game_over":True,"new_round":False,"round":0}

    di = g["current_drawer"]
    if di in g["players"]:
        g["players"][di]["rounds_drawn"] += 1

        # Bonus if everyone guessed
        if all_guessed(g):
            g["players"][di]["score"] += POINTS_BONUS

    g["turn_index"] += 1
    tpr = len(g["order"])
    new_round = False

    if g["turn_index"] >= tpr * g["round"]:
        g["round"] += 1
        new_round   = True

    if g["round"] > ROUNDS:
        g["status"] = "ended"
        return {"game_over":True,"new_round":False,"round":g["round"]-1}

    _assign_drawer(g)
    return {"game_over":False,"new_round":new_round,"round":g["round"]}


def reveal_hint(chat_id: int) -> str:
    g = get_draw_game(chat_id)
    if not g or not g["current_word"]:
        return ""
    g["hint_level"] = min(g["hint_level"]+1, len(g["current_word"])-1)
    return word_with_hint(g["current_word"], g["hint_level"])


# ── Scoring ───────────────────────────────────────────────

def get_scoreboard(game: dict) -> list[dict]:
    return sorted(game["players"].values(), key=lambda p: p["score"], reverse=True)


def get_winner(game: dict) -> dict | None:
    b = get_scoreboard(game)
    return b[0] if b else None


def format_scoreboard(game: dict) -> str:
    board   = get_scoreboard(game)
    medals  = ["🥇","🥈","🥉"]
    lines   = []
    for i, p in enumerate(board):
        m   = medals[i] if i<3 else f"{i+1}."
        uid = p["id"]
        lines.append(
            f'{m} <a href="tg://user?id={uid}">{p["name"]}</a> — '
            f'<b>{p["score"]}</b> pts'
        )
    return "\n".join(lines) if lines else "No scores yet."