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

import json
from pathlib import Path


_LOCALE_PATH = Path(__file__).parent / "en.json"


def _load_locale():
    with open(_LOCALE_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


_TEXTS = _load_locale()


def get_text(key: str, **kwargs) -> str:
    text = _TEXTS.get(key, key)

    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text

    return text