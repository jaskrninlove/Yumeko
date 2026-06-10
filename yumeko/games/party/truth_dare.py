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

import random
from datetime import datetime


active_truth_dares = {}

TRUTH_XP = 5
DARE_XP = 10
DARE_COINS = 15


TRUTHS = [
    "What is one secret you have never told this group?",
    "Who in this chat do you trust the most?",
    "What is your most embarrassing moment?",
    "Have you ever had a crush on someone online?",
    "What is one thing you pretend to like but actually don't?",
    "Who was the last person you stalked on social media?",
    "What is your biggest fear in love?",
    "What is one message you regret sending?",
    "Who in this group has the best vibe?",
    "What is something cute you secretly like?",
]


DARES = [
    "Send a voice note saying: Yumeko owns this game.",
    "Compliment the person above your message.",
    "Use only emojis for your next 3 messages.",
    "Change your name for 10 minutes.",
    "Send the most dramatic line you can think of.",
    "Act like Yumeko for one message.",
    "Tell the group: I accept defeat, but only for now.",
    "Send a message using only capital letters.",
    "Praise your rival in this group.",
    "Say: I challenge fate, and fate challenged me back.",
]


TRUTH_REACTIONS = [
    "🎭 Yumeko listens carefully...\n\nInteresting answer, darling. I will remember that. ♡",
    "🎭 Yumeko smiles mysteriously...\n\nHonesty looks good on you.",
    "🎭 Yumeko leans closer...\n\nThat answer was more interesting than expected. ♠️",
]


DARE_COMPLETE_REACTIONS = [
    "🎲 Yumeko applauds softly...\n\nChallenge completed. Not bad, darling. ♡",
    "🎭 Yumeko smiles proudly...\n\nYou accepted fate and survived.",
    "🎲 Yumeko giggles...\n\nBrave move. The table respects you now. ♠️",
]


DARE_SKIP_REACTIONS = [
    "🎭 Yumeko sighs softly...\n\nSkipping already? Fate expected more, darling.",
    "🎲 Yumeko takes the card back...\n\nMaybe next time you will be braver. ♠️",
]


def get_truth():
    return random.choice(TRUTHS)


def get_dare():
    return random.choice(DARES)


def get_random_truth_dare():
    choice = random.choice(["truth", "dare"])

    if choice == "truth":
        return "truth", get_truth()

    return "dare", get_dare()


def create_truth_session(chat_id: int, user_id: int, text: str):
    active_truth_dares[(chat_id, user_id)] = {
        "type": "truth",
        "text": text,
        "created_at": datetime.utcnow(),
        "answered": False,
    }


def create_dare_session(chat_id: int, user_id: int, text: str):
    active_truth_dares[(chat_id, user_id)] = {
        "type": "dare",
        "text": text,
        "created_at": datetime.utcnow(),
        "answered": False,
    }


def get_session(chat_id: int, user_id: int):
    return active_truth_dares.get((chat_id, user_id))


def remove_session(chat_id: int, user_id: int):
    active_truth_dares.pop((chat_id, user_id), None)


def random_truth_reaction():
    return random.choice(TRUTH_REACTIONS)


def random_dare_complete_reaction():
    return random.choice(DARE_COMPLETE_REACTIONS)


def random_dare_skip_reaction():
    return random.choice(DARE_SKIP_REACTIONS)