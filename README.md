# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jaskaran Singh
#
#  Developer  : Jaskaran Singh
#  Project    : Yumeko Games Bot
#  Version    : 1.0.0
#
#  GitHub     : Private
#  License    : MIT License
#
#  This file is part of Yumeko Games Bot.
#  Unauthorized removal of this notice is discouraged.
#
#  © 2026 Jaskaran Singh. All Rights Reserved.
# ==========================================================

<div align="center">

<h1>🎮 Yumeko Games Bot</h1>

<p><em>The ultimate gaming companion for your Discord server</em></p>

![Version](https://img.shields.io/badge/version-1.0.0-blueviolet?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)
![Games](https://img.shields.io/badge/Games-40+-ff69b4?style=for-the-badge)

<br/>

> **Yumeko** is an advanced, feature-rich Discord gaming bot packed with **40+ games and activities** to keep your community entertained — from classic card games and trivia to strategic duels and economy systems.

</div>

---

## 📋 Table of Contents

- [Features](#-features)
- [Games Catalogue](#-games-catalogue)
- [Getting Started](#-getting-started)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Deployment](#-deployment)
- [Commands](#-commands)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎮 **40+ Games** | A massive library of games for every type of player |
| 🏆 **Leaderboards** | Server-wide rankings and global scoreboards |
| 💰 **Economy System** | Earn coins, bet, and spend across games |
| 🎲 **Multiplayer** | Challenge friends in real-time duels |
| 📊 **Stats Tracking** | Detailed per-user game statistics |
| 🛡️ **Anti-Cheat** | Built-in cooldowns and fairness enforcement |
| ⚡ **Fast & Reliable** | Optimized for low latency and high uptime |
| 🔧 **Configurable** | Per-server settings for full customization |

---

## 🎮 Games Catalogue

### 🃏 Card Games
- **Blackjack** — Beat the dealer to 21 without going bust
- **Poker** — Classic Texas Hold'em against the bot or friends
- **War** — Fast-paced card flipping battle
- **Snap** — React fast to matching cards
- **Higher or Lower** — Predict the next card's value

### 🎲 Dice & Chance
- **Roll Dice** — Single or multi-dice rolls with custom sides
- **Coin Flip** — Heads or tails with optional betting
- **Slots** — Spin the reels and hit the jackpot
- **Roulette** — Place bets on numbers, colors, or ranges
- **Lucky Number** — Pick a number and test your luck

### 🧠 Trivia & Knowledge
- **Trivia** — Multi-category quiz with difficulty levels
- **True or False** — Quick-fire fact checking
- **Anagram** — Unscramble the letters to find the word
- **Hangman** — Classic word guessing game
- **Word Chain** — Keep the chain going with the last letter

### ⚔️ Strategy & Skill
- **TicTacToe** — 1v1 grid domination
- **Connect Four** — Drop pieces to form a line of four
- **Chess Puzzles** — Solve board positions
- **Battleship** — Sink the enemy fleet
- **Minesweeper** — Defuse the board without hitting a mine

### 🏃 Reaction & Speed
- **Type Race** — Who can type the phrase fastest?
- **Click Race** — Fastest reaction time wins
- **Memory Game** — Match pairs from a hidden grid
- **Fast Math** — Solve arithmetic under pressure
- **Emoji Quiz** — Guess the word from emoji clues

### 🎯 Arcade
- **Number Guess** — Classic high-low number guessing
- **Rock Paper Scissors** — Best of 3 against the bot or a friend
- **8-Ball** — Ask the magic ball your questions
- **Riddles** — Solve tricky riddles for coins
- **Would You Rather** — Vote and see community results

### 💰 Economy Games
- **Coinflip Bet** — Wager your coins on a flip
- **Heist** — Coordinate a robbery with server members
- **Rob** — Attempt to steal coins from another user
- **Daily Rewards** — Claim your daily coin bonus
- **Shop** — Spend coins on roles and perks

### 🌐 Miscellaneous
- **Akinator** — Think of a character and let Yumeko guess it
- **Truth or Dare** — Party-ready prompts for your server
- **Compliment Battle** — Vote for the best compliment
- **Server Bingo** — Community-wide bingo events
- **Random Story** — Collaborative AI-powered story building

---

## 🚀 Getting Started

### Prerequisites

- Python **3.10** or higher
- A Discord Bot Token ([Discord Developer Portal](https://discord.com/developers/applications))
- Git

### Quick Start

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd yumeko

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
.venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp sample.env .env
# Edit .env with your token and config

# 5. Run the bot
python -m yumeko
```

---

## 🔧 Installation

### Local Development

```bash
pip install -r requirements.txt
```

### Docker

```bash
# Build the image
docker build -t yumeko .

# Run the container
docker run --env-file .env yumeko
```

### Docker Compose (Recommended)

```bash
docker-compose up -d
```

---

## ⚙️ Configuration

Copy `sample.env` to `.env` and fill in your values:

```env
# ── Discord ────────────────────────────────────────────
DISCORD_TOKEN=your_bot_token_here
PREFIX=!

# ── Bot Settings ───────────────────────────────────────
BOT_NAME=Yumeko
LOG_LEVEL=INFO

# ── Economy ────────────────────────────────────────────
STARTING_COINS=500
DAILY_REWARD=100

# ── Database (if applicable) ───────────────────────────
DATABASE_URL=sqlite:///yumeko.db
```

> ⚠️ **Never commit your `.env` file.** It is already included in `.gitignore`.

---

## ☁️ Deployment

### Railway (Recommended)

1. Push your code to GitHub
2. Connect the repo to [Railway](https://railway.app)
3. Add your environment variables in the Railway dashboard
4. Railway will auto-detect `railway.json` and deploy

The included `railway.json` is already configured for seamless deployment.

### Heroku

```bash
# Login and create app
heroku login
heroku create your-app-name

# Set environment variables
heroku config:set DISCORD_TOKEN=your_token

# Deploy
git push heroku main
```

The included `Procfile` handles the worker process automatically:

```
worker: python -m yumeko
```

### Docker Compose (Self-Hosted)

```bash
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## 🕹️ Commands

| Command | Description |
|---|---|
| `!help` | Show all available commands |
| `!games` | Browse the full games list |
| `!play <game>` | Start a specific game |
| `!leaderboard` | View server rankings |
| `!balance` | Check your coin balance |
| `!daily` | Claim your daily reward |
| `!bet <amount>` | Wager coins on a game |
| `!stats [@user]` | View game statistics |
| `!shop` | Browse the coin shop |
| `!settings` | Configure bot for your server *(Admin only)* |

> The default prefix is `!`. It can be changed per server by an admin.

---

## 📁 Project Structure

```
yumeko/
├── yumeko/              # Main bot package
│   ├── __init__.py
│   ├── bot.py           # Bot initialization & events
│   ├── cogs/            # Command groups (games, economy, etc.)
│   └── utils/           # Helpers, database, formatting
├── .env                 # Your local secrets (not committed)
├── sample.env           # Template for environment variables
├── Dockerfile           # Docker image definition
├── docker-compose.yml   # Multi-container setup
├── Procfile             # Railway/Heroku process definition
├── railway.json         # Railway deployment config
├── requirements.txt     # Python dependencies
├── yumeko.log           # Runtime log file
└── README.md            # You are here
```

---

## 🤝 Contributing

This is a private project. Contributions are by invitation only.

If you have been granted access:

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Commit your changes: `git commit -m "feat: add your feature"`
3. Push the branch: `git push origin feature/your-feature`
4. Open a pull request for review

Please follow the existing code style and add docstrings to any new commands or cogs.

---

## 📜 License

This project is licensed under the **MIT License**.
See the [LICENSE](LICENSE) file for full details.

---

<div align="center">

Made with ❤️ by **Jaskaran Singh**

© 2026 Jaskaran Singh. All Rights Reserved.

</div>