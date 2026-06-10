# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass  |  Version 3.0.0
# ==========================================================

GAMES_PER_PAGE = 8

GAMES = {
    # ── ⚔️ MULTIPLAYER / PARTY ─────────────────────────────
    "reaction": {
        "title": "⚡ Reaction Battle", "category": "multiplayer",
        "command": "/reaction",
        "caption": "A single spark. The fastest soul takes the crown.",
        "rules": "Wait for the real button. Tap it before anyone else. Fake signals may appear.",
        "rewards": "Winner earns coins + XP.",
    },
    "typing": {
        "title": "⌨️ Typing Race", "category": "multiplayer",
        "command": "/typingrace",
        "caption": "Speed, accuracy, and trembling fingers.",
        "rules": "Type the sentence exactly. First correct player wins.",
        "rewards": "Winner earns coins + XP.",
    },
    "quizbattle": {
        "title": "🧠 Quiz Battle", "category": "multiplayer",
        "command": "/quiz",
        "caption": "Ten questions. One fastest mind. No mercy.",
        "rules": "Tap the right answer. First correct answer gets bonus points.",
        "rewards": "Winner earns coins + XP.",
    },
    "hotpotato": {
        "title": "🥔 Hot Potato", "category": "multiplayer",
        "command": "/hotpotato",
        "caption": "Pass it fast. Do not be the one holding it.",
        "rules": "Tap pass before the hidden timer explodes. Last survivor wins.",
        "rewards": "Survivors earn rewards.",
    },
    "draw": {
        "title": "🎨 Draw & Guess", "category": "multiplayer",
        "command": "/draw",
        "caption": "One player draws. Everyone else guesses. Chaos follows.",
        "rules": "Artist draws the secret word. Others guess in group chat.",
        "rewards": "Artist and first guesser earn XP/coins.",
    },
    "poisoncandy": {
        "title": "☠️ Candy Poison", "category": "multiplayer",
        "command": "/candy",
        "caption": "Sweetness hides danger. Trust no candy.",
        "rules": "Players secretly poison one candy in DM. Then everyone takes turns eating candies. Poison eliminates.",
        "rewards": "Last survivor wins coins + XP.",
    },
    "mysterybox": {
        "title": "🎁 Mystery Box Royale", "category": "multiplayer",
        "command": "/box",
        "caption": "Every box hides a blessing... or a disaster.",
        "rules": "Open boxes on your turn. Boxes may contain coins, XP, shields, crowns, traps, death, or jackpot.",
        "rewards": "Winner bonus + box rewards.",
    },
    "russianroulette": {
        "title": "🔫 Russian Roulette", "category": "multiplayer",
        "command": "/rr",
        "caption": "Six chambers. One bullet. One survivor.",
        "rules": "Players pull the trigger in turns. Empty chamber survives. Bullet eliminates.",
        "rewards": "Last survivor earns coins + XP.",
    },
    "higherlower": {
        "title": "🃏 Higher or Lower", "category": "multiplayer",
        "command": "/hl",
        "caption": "One card. Two choices. Everything on the line.",
        "rules": "Vote higher or lower before the next card is revealed. Wrong guesses cost lives.",
        "rewards": "Most points wins coins + XP.",
    },
    "safecracker": {
        "title": "🔐 Safe Cracker", "category": "multiplayer",
        "command": "/safe",
        "caption": "Guess the secret code before the vault rejects you.",
        "rules": "Build symbol guesses. Bulls mean correct position, cows mean correct symbol wrong position.",
        "rewards": "Fastest cracker gets bonus coins + XP.",
    },
    "minesweeper": {
        "title": "💎 Minesweeper", "category": "multiplayer",
        "command": "/ms",
        "caption": "One step forward. One mistake away from disaster.",
        "rules": "Each player gets a board. Reveal safe tiles, avoid mines, survive longer than rivals.",
        "rewards": "Winner earns coins + XP. Perfect clear gives bonus.",
    },

    # ── ♟ STRATEGY BOARD GAMES ─────────────────────────────
    "connect4": {
        "title": "🔴 Connect Four", "category": "strategy",
        "command": "/connect4",
        "caption": "Four pieces. Infinite possibilities. One winner.",
        "rules": "Drop discs into columns. First to connect four horizontally, vertically, or diagonally wins.",
        "rewards": "Winner earns coins + XP.",
    },
    "chainreaction": {
        "title": "⚛ Chain Reaction", "category": "strategy",
        "command": "/chain",
        "caption": "One orb becomes chaos. Chaos chooses a favorite.",
        "rules": "Place orbs. Overloaded cells explode and capture nearby cells. Last player with orbs wins.",
        "rewards": "Winner earns coins + XP.",
    },
    "gomoku": {
        "title": "⚫ Gomoku", "category": "strategy",
        "command": "/gomoku",
        "caption": "Five stones. One perfect line. One beautiful victory.",
        "rules": "Black and White place stones. First to connect five horizontally, vertically, or diagonally wins.",
        "rewards": "Winner earns coins + XP.",
    },
    "battleship": {
        "title": "🚢 Battleship Royale", "category": "strategy",
        "command": "/sea",
        "caption": "The sea is calm. The cannons are loaded.",
        "rules": "Ships are hidden. Fire at enemy waters. Hits grant another turn. Sink all ships to win.",
        "rewards": "Winner earns coins + XP.",
    },
    "tictactoe": {
        "title": "❌ Tic Tac Toe", "category": "strategy",
        "command": "/tictactoe",
        "caption": "Simple grid. Sharp mind. Quick victory.",
        "rules": "Reply to a player and start. First to make three in a row wins.",
        "rewards": "Winner earns coins + XP.",
    },

    # ── 🔤 WORD GAMES ──────────────────────────────────────
    "wordchain": {
        "title": "🔤 Word Chain", "category": "word",
        "command": "/wordchain",
        "caption": "Every word becomes a chain around your fate.",
        "rules": "Your word must start with the last letter of the previous word. Timeout eliminates.",
        "rewards": "Winner earns coins + XP.",
    },
    "bombparty": {
        "title": "💣 Bomb Party", "category": "word",
        "command": "/bombparty",
        "caption": "The bomb is hungry. Feed it the right word.",
        "rules": "Word must contain given letters. Timeout or invalid word costs lives.",
        "rewards": "Last survivor earns coins + XP.",
    },

    # ── 🏎 WEBAPP / SPORTS / MINI ──────────────────────────
    "racing": {
        "title": "🏎 Yumeko Racing", "category": "mini",
        "command": "/race",
        "caption": "Speed is not everything. Surviving the track is.",
        "rules": "Open the racing track, dodge traffic, collect coins, use nitro, submit score.",
        "rewards": "Score-based coins + XP.",
    },
    "raceduel": {
        "title": "🏁 Racing Duel", "category": "mini",
        "command": "/raceduel",
        "caption": "Two engines. One finish line.",
        "rules": "Reply to a player with /raceduel. Tap accelerate and nitro to reach 100%.",
        "rewards": "Winner earns coins + XP.",
    },
    "football": {
        "title": "⚽ Football Shootout", "category": "mini",
        "command": "/football",
        "caption": "One shot. One keeper. One beautiful gamble.",
        "rules": "Take shots and try to score more than your rival.",
        "rewards": "Winner earns coins + XP.",
    },
    "hockey": {
        "title": "🏒 Hockey Shootout", "category": "mini",
        "command": "/hockey",
        "caption": "Cold ice. Hot nerves.",
        "rules": "Shoot the puck and beat the keeper.",
        "rewards": "Winner earns coins + XP.",
    },
    "bowling": {
        "title": "🎳 Bowling", "category": "mini",
        "command": "/bowling",
        "caption": "Roll fate down the lane.",
        "rules": "Roll and score. Higher score wins.",
        "rewards": "Winner earns coins + XP.",
    },
    "boxing": {
        "title": "🥊 Boxing", "category": "mini",
        "command": "/boxing",
        "caption": "Two fists. One winner.",
        "rules": "Duel another player and trade blows until one falls.",
        "rewards": "Winner earns coins + XP.",
    },
    "rps": {
        "title": "✂️ RPS Duel", "category": "mini",
        "command": "/rps",
        "caption": "One hand. One choice. One tiny gamble.",
        "rules": "Reply to someone with /rps and choose rock, paper, or scissors.",
        "rewards": "Winner earns coins + XP.",
    },
    "dice": {
        "title": "🎲 Dice", "category": "mini",
        "command": "/dice",
        "caption": "Let the cube fall. Let fate speak.",
        "rules": "Roll dice or guess the outcome.",
        "rewards": "Correct guess gives rewards.",
    },
    "slot": {
        "title": "🎰 Slot Machine", "category": "mini",
        "command": "/slot",
        "caption": "Spin the reels. Chase the scream of jackpot.",
        "rules": "Bet coins and match symbols.",
        "rewards": "Jackpots multiply your bet.",
    },
    "toss": {
        "title": "🪙 Coin Toss", "category": "mini",
        "command": "/toss heads",
        "caption": "Heads or tails, darling.",
        "rules": "Guess heads or tails.",
        "rewards": "Correct guess wins.",
    },

    # ── 💞 ROMANCE ─────────────────────────────────────────
    "propose": {
        "title": "💌 Propose", "category": "romance",
        "command": "/propose",
        "caption": "A heart placed on the table is the riskiest bet.",
        "rules": "Reply to someone with /propose or /marry.",
        "rewards": "Creates a couple if accepted.",
    },
    "divorce": {
        "title": "💔 Divorce", "category": "romance",
        "command": "/divorce",
        "caption": "Some stories end with one last card.",
        "rules": "Use /divorce to end marriage.",
        "rewards": "Frees both users.",
    },
    "spouse": {
        "title": "💕 Couple Profile", "category": "romance",
        "command": "/spouse",
        "caption": "A little book of love and devotion.",
        "rules": "Use /spouse, /married, or /coupleprofile.",
        "rewards": "Shows couple stats.",
    },

    # ── 💰 ECONOMY / PROGRESS ──────────────────────────────
    "balance": {
        "title": "💰 Wallet", "category": "economy",
        "command": "/balance",
        "caption": "Every coin has a story.",
        "rules": "Use /balance, /bal, or /wallet.",
        "rewards": "Shows coins, XP, level, and rank.",
    },
    "daily": {
        "title": "🎁 Daily Reward", "category": "economy",
        "command": "/daily",
        "caption": "A gift from Yumeko every 24 hours.",
        "rules": "Claim once per day.",
        "rewards": "Coins + XP + streak bonus.",
    },
    "work": {
        "title": "💼 Work", "category": "economy",
        "command": "/work",
        "caption": "Hard work is cute. Gambling is faster.",
        "rules": "Use /work once per cooldown.",
        "rewards": "Random coins + XP.",
    },
    "crime": {
        "title": "🦹 Crime", "category": "economy",
        "command": "/crime",
        "caption": "Risk your luck for a darker reward.",
        "rules": "Crime can succeed or fail.",
        "rewards": "Success gives coins. Failure may lose coins.",
    },
    "profile": {
        "title": "👤 Profile", "category": "progress",
        "command": "/profile",
        "caption": "Every game leaves a mark on your soul.",
        "rules": "Shows stats, coins, XP, level, and win rate.",
        "rewards": "Track your journey.",
    },
    "leaderboard": {
        "title": "🏆 Global Rankings", "category": "progress",
        "command": "/leaderboard",
        "caption": "The throne remembers every victory.",
        "rules": "Use /leaderboard coins, xp, wins, couples, mafia, reaction.",
        "rewards": "Community fame and bragging rights.",
    },
    "achievements": {
        "title": "🎖 Achievements", "category": "progress",
        "command": "/achievements",
        "caption": "Badges prove you dared to play.",
        "rules": "Shows unlockable achievements.",
        "rewards": "Earn badges by playing.",
    },

    # ── 🎭 MAFIA ───────────────────────────────────────────
    "mafia": {
        "title": "🎭 Mafia V3", "category": "mafia",
        "command": "/mafia",
        "caption": "Masks, lies, secret roles, betrayal, and one beautiful murder.",
        "rules": "Secret roles. Mafia kills at night. Villagers vote by day.",
        "rewards": "Winning team earns rewards. MVP gets bonus.",
    },
    "mafiarules": {
        "title": "📜 Mafia Rules", "category": "mafia",
        "command": "/mafiarules",
        "caption": "Trust is the first thing to die.",
        "rules": "Explains Mafia roles, phases, and win conditions.",
        "rewards": "Knowledge is dangerous.",
    },
}

CATEGORIES = {
    "all": {"title": "🎮 All Games", "emoji": "🎮"},
    "multiplayer": {"title": "⚔️ Multiplayer", "emoji": "⚔️"},
    "strategy": {"title": "♟ Strategy", "emoji": "♟"},
    "word": {"title": "🔤 Word Games", "emoji": "🔤"},
    "mini": {"title": "🎲 Mini / Sports", "emoji": "🎲"},
    "romance": {"title": "💞 Romance", "emoji": "💞"},
    "economy": {"title": "💰 Economy", "emoji": "💰"},
    "progress": {"title": "🏆 Progress", "emoji": "🏆"},
    "mafia": {"title": "🎭 Mafia", "emoji": "🎭"},
}


def get_all_categories():
    return CATEGORIES


def get_category(cid):
    return CATEGORIES.get(cid)


def get_all_games():
    return GAMES


def get_game(gid):
    return GAMES.get(gid)


def get_games_by_category(category_id: str):
    if category_id == "all":
        return GAMES
    return {gid: g for gid, g in GAMES.items() if g["category"] == category_id}


def paginated_games(category_id: str = "all", page: int = 0):
    games = list(get_games_by_category(category_id).items())
    start = page * GAMES_PER_PAGE
    return games[start:start + GAMES_PER_PAGE], len(games)


def count_total():
    return len(GAMES)


def count_by_category(cid):
    return len(get_games_by_category(cid))