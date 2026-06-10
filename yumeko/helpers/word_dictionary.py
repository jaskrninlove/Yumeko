# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
# ==========================================================

from pathlib import Path
import re


_WORDS_CACHE = None

WORDS_PATHS = [
    Path("words.txt"),
    Path("yumeko/words.txt"),
    Path("yumeko/data/words.txt"),
    Path("yumeko/assets/words.txt"),
]


def clean_word(word: str) -> str:
    if not word:
        return ""

    word = word.strip().lower()
    word = re.sub(r"[^a-z]", "", word)
    return word


def load_words() -> set:
    global _WORDS_CACHE

    if _WORDS_CACHE is not None:
        return _WORDS_CACHE

    words = set()

    for path in WORDS_PATHS:
        if path.exists():
            with open(path, "r", encoding="utf-8", errors="ignore") as file:
                for line in file:
                    word = clean_word(line)
                    if len(word) >= 2:
                        words.add(word)
            break

    _WORDS_CACHE = words
    return _WORDS_CACHE


def is_valid_dictionary_word(word: str) -> bool:
    word = clean_word(word)

    if not word:
        return False

    words = load_words()

    if not words:
        return False

    return word in words