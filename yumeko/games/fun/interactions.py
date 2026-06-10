# ==========================================================
#  Yumeko Games Bot — Action Texts
#  Copyright (c) 2026 Jass
#
#  Developer  : Jass
#  Project    : Yumeko Games Bot
#  Version    : 1.0.1
#
#  GitHub     : Private
#  License    : MIT License
#
#  This file is part of Yumeko Games Bot.
#  Unauthorized removal of this notice is discouraged.
#
#  © 2026 Jass. All Rights Reserved.
# ==========================================================

import html
import random


ACTIONS = {
    "hug": {
        "emoji": "🤗",
        "score": "+10 Affection",
        "templates": [
            "🎭 <b>Yumeko smiles softly...</b>\n\n<b>{user}</b> pulls <b>{target}</b> into a warm embrace.\n\nSome hugs say more than words ever could. ♡",
            "🎭 <b>Yumeko tilts her head...</b>\n\n<b>{user}</b> wraps <b>{target}</b> in a gentle hug.\n\nHow sweet, darling~",
        ],
        "self": "🎭 <b>Yumeko watches quietly...</b>\n\n<b>{user}</b> hugs themselves.\n\nA little self-love never hurts. ♡",
        "bot": "🎭 <b>Yumeko smiles mysteriously...</b>\n\n<b>{user}</b> tries to hug <b>Yumeko</b>.\n\nHow adorable. ♡",
    },
    "kiss": {
        "emoji": "💋",
        "score": "+15 Romance",
        "templates": [
            "🎭 <b>Yumeko covers her smile...</b>\n\n<b>{user}</b> steals a tiny kiss from <b>{target}</b>.\n\nHow daring~ ♡",
            "🎭 <b>Yumeko giggles softly...</b>\n\n<b>{user}</b> gives <b>{target}</b> a sweet little kiss.\n\nThe game just became interesting. ♡",
        ],
        "self": "🎭 <b>Yumeko blinks...</b>\n\n<b>{user}</b> tried to kiss themselves.\n\nConfidence level: dangerous. ♡",
        "bot": "🎭 <b>Yumeko steps back gracefully...</b>\n\n<b>{user}</b> tries to kiss <b>Yumeko</b>.\n\nWin a game first, darling. ♠️",
    },
    "cuddle": {
        "emoji": "☁️",
        "score": "+12 Warmth",
        "templates": [
            "🎭 <b>Yumeko giggles softly...</b>\n\n<b>{user}</b> cuddles up beside <b>{target}</b>.\n\nThe world feels a little warmer now. ☁️",
            "🎭 <b>Yumeko smiles...</b>\n\n<b>{user}</b> pulls <b>{target}</b> close for a cozy cuddle.\n\nSoft moments are rare treasures. ♡",
        ],
        "self": "🎭 <b>Yumeko smiles gently...</b>\n\n<b>{user}</b> cuddles themselves.\n\nCozy, lonely, but cute. ♡",
        "bot": "🎭 <b>Yumeko laughs quietly...</b>\n\n<b>{user}</b> tries to cuddle <b>Yumeko</b>.\n\nYou're brave, darling. ♡",
    },
    "slap": {
        "emoji": "👋",
        "score": "+8 Drama",
        "templates": [
            "🎭 <b>Yumeko raises an eyebrow...</b>\n\n<b>{user}</b> delivers a dramatic slap to <b>{target}</b>.\n\nThat must have hurt. ♠️",
            "🎭 <b>Yumeko watches with interest...</b>\n\n<b>{user}</b> slaps <b>{target}</b> like a final boss.\n\nSuch chaos. ♠️",
        ],
        "self": "🎭 <b>Yumeko pauses...</b>\n\n<b>{user}</b> slapped themselves.\n\nThat was... unexpected.",
        "bot": "🎭 <b>Excuse me?</b>\n\n<b>{user}</b> tries to slap <b>Yumeko</b>, but she dodges effortlessly.\n\nNice try, darling. ♡",
    },
    "punch": {
        "emoji": "💥",
        "score": "+10 Chaos",
        "templates": [
            "🎭 <b>Yumeko steps back...</b>\n\n<b>{user}</b> throws a punch at <b>{target}</b>.\n\nViolence is not the answer... but it was definitely a response. 💥",
            "🎭 <b>Yumeko smirks...</b>\n\n<b>{user}</b> punches <b>{target}</b> with dramatic energy.\n\nThe arena is getting louder. ♠️",
        ],
        "self": "🎭 <b>Yumeko sighs...</b>\n\n<b>{user}</b> punched themselves.\n\nSelf-battle unlocked. 💥",
        "bot": "🎭 <b>Yumeko catches the punch with two fingers.</b>\n\nToo slow, darling. ♠️",
    },
    "pat": {
        "emoji": "🫳",
        "score": "+8 Comfort",
        "templates": [
            "🎭 <b>Yumeko smiles...</b>\n\n<b>{user}</b> gently pats <b>{target}</b>'s head.\n\nGood job, darling. ♡",
            "🎭 <b>Yumeko nods softly...</b>\n\n<b>{user}</b> gives <b>{target}</b> a comforting headpat.\n\nSo wholesome. ♡",
        ],
        "self": "🎭 <b>Yumeko smiles...</b>\n\n<b>{user}</b> pats themselves.\n\nYou did well today. ♡",
        "bot": "🎭 <b>Yumeko accepts the headpat.</b>\n\nOnly because it was cute. ♡",
    },
    "bonk": {
        "emoji": "🔨",
        "score": "+9 Discipline",
        "templates": [
            "🎭 <b>Yumeko lifts a tiny hammer...</b>\n\n<b>{user}</b> bonks <b>{target}</b>.\n\nBack to the game, darling. 🔨",
            "🎭 <b>Yumeko laughs...</b>\n\n<b>{user}</b> sends <b>{target}</b> to bonk jail.\n\nNo escape. ♠️",
        ],
        "self": "🎭 <b>Yumeko stares...</b>\n\n<b>{user}</b> bonked themselves.\n\nSelf-control achieved.",
        "bot": "🎭 <b>Yumeko takes the hammer away.</b>\n\nNo bonking the dealer, darling. ♠️",
    },
    "bite": {
        "emoji": "🦷",
        "score": "+7 Mischief",
        "templates": [
            "🎭 <b>Yumeko grins...</b>\n\n<b>{user}</b> bites <b>{target}</b> playfully.\n\nCareful, darling~",
            "🎭 <b>Yumeko watches closely...</b>\n\n<b>{user}</b> gives <b>{target}</b> a tiny bite.\n\nMischief detected. ♡",
        ],
        "self": "🎭 <b>Yumeko blinks...</b>\n\n<b>{user}</b> bit themselves.\n\nCuriosity can be dangerous.",
        "bot": "🎭 <b>Yumeko steps away...</b>\n\nBiting me?\n\nHow fearless. ♠️",
    },
    "tickle": {
        "emoji": "😂",
        "score": "+10 Laughter",
        "templates": [
            "🎭 <b>Yumeko giggles...</b>\n\n<b>{user}</b> tickles <b>{target}</b> until they can't stop laughing.",
            "🎭 <b>Yumeko claps softly...</b>\n\n<b>{user}</b> starts a tickle attack on <b>{target}</b>.\n\nCritical hit: laughter. 😂",
        ],
        "self": "🎭 <b>Yumeko laughs...</b>\n\n<b>{user}</b> tried to tickle themselves.\n\nDid it work?",
        "bot": "🎭 <b>Yumeko is immune to tickles.</b>\n\nPerks of being the host. ♠️",
    },
    "blush": {
        "emoji": "😳",
        "score": "+6 Shyness",
        "templates": [
            "🎭 <b>Yumeko notices...</b>\n\n<b>{user}</b> makes <b>{target}</b> blush.\n\nHow cute. ♡",
            "🎭 <b>Yumeko smiles knowingly...</b>\n\n<b>{target}</b> blushes because of <b>{user}</b>.\n\nInteresting~",
        ],
        "self": "🎭 <b>Yumeko whispers...</b>\n\n<b>{user}</b> blushes alone.\n\nSecret thoughts, perhaps?",
        "bot": "🎭 <b>Yumeko hides her smile...</b>\n\n<b>{user}</b> tries to make <b>Yumeko</b> blush.\n\nMaybe it worked. ♡",
    },
    "highfive": {
        "emoji": "✋",
        "score": "+5 Teamwork",
        "templates": [
            "🎭 <b>Yumeko cheers...</b>\n\n<b>{user}</b> gives <b>{target}</b> a perfect high-five.\n\nTeamwork looks good on you. ✋",
            "🎭 <b>Yumeko smiles brightly...</b>\n\n<b>{user}</b> and <b>{target}</b> share a clean high-five.\n\nNice one. ♡",
        ],
        "self": "🎭 <b>Yumeko watches...</b>\n\n<b>{user}</b> high-fives the air.\n\nThe air appreciates it.",
        "bot": "🎭 <b>Yumeko gives you a graceful high-five.</b>\n\nWell played, darling. ♡",
    },
    "feed": {
        "emoji": "🍰",
        "score": "+9 Sweetness",
        "templates": [
            "🎭 <b>Yumeko smiles...</b>\n\n<b>{user}</b> feeds <b>{target}</b> something sweet.\n\nSharing is adorable. 🍰",
            "🎭 <b>Yumeko watches softly...</b>\n\n<b>{user}</b> offers <b>{target}</b> a little treat.\n\nHow gentle. ♡",
        ],
        "self": "🎭 <b>Yumeko nods...</b>\n\n<b>{user}</b> feeds themselves.\n\nSelf-care is important. 🍰",
        "bot": "🎭 <b>Yumeko accepts the treat.</b>\n\nYou have good taste, darling. ♡",
    },
}


def get_action(action: str):
    return ACTIONS.get((action or "").lower())


def safe_name(name: str | None, fallback: str = "Someone"):
    return html.escape(name or fallback)


def make_user_mention(user, fallback: str = "Someone"):
    if not user:
        return safe_name(fallback)

    name = safe_name(getattr(user, "first_name", None), fallback)
    user_id = getattr(user, "id", None)

    if not user_id:
        return name

    return f'<a href="tg://user?id={user_id}">{name}</a>'


def make_interaction_text(action: str, user: str, target: str, mode: str = "normal"):
    data = get_action(action)

    if not data:
        return None

    user = safe_name(user, "Someone")
    target = safe_name(target, "Someone")

    if mode == "self":
        return data["self"].format(user=user, target=target)

    if mode == "bot":
        return data["bot"].format(user=user, target=target)

    template = random.choice(data["templates"])

    return (
        template.format(user=user, target=target)
        + f"\n\n{data['emoji']} <b>{data['score']}</b>"
    )


def make_interaction_text_from_users(action: str, user, target_user=None, mode: str = "normal", target_name: str | None = None):
    user_text = make_user_mention(user, "Someone")

    if target_user:
        target_text = make_user_mention(target_user, "Someone")
    else:
        target_text = safe_name(target_name, "Someone")

    data = get_action(action)

    if not data:
        return None

    if mode == "self":
        return data["self"].format(user=user_text, target=target_text)

    if mode == "bot":
        return data["bot"].format(user=user_text, target=target_text)

    template = random.choice(data["templates"])

    return (
        template.format(user=user_text, target=target_text)
        + f"\n\n{data['emoji']} <b>{data['score']}</b>"
    )