# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
# ==========================================================

from yumeko.games.mafia.game import (
    JOIN_TIME,
    NIGHT_TIME,
    DISCUSSION_TIME,
    VOTE_TIME,
    MIN_PLAYERS,
    MAX_PLAYERS,
    WIN_COINS,
    WIN_XP,
    LOSE_XP,
    JESTER_COINS,
    JESTER_XP,
    role_name,
    format_players,
    format_alive,
    format_roles,
)


# ──────────────────────────────────────────────
#  Role Guides
# ──────────────────────────────────────────────

ROLE_GUIDES = {
    "mafia": {
        "title": "🔪 Shadow Dealer",
        "goal": "Eliminate the town until Mafia equals or outnumbers them.",
        "ability": "Every night, vote with your Mafia team to choose one victim.",
        "tip": "Act innocent. Smile softly. Let others accuse each other.",
    },
    "godfather": {
        "title": "🕶 Crimson Monarch",
        "goal": "Lead the shadows and bring Mafia to victory.",
        "ability": "Works with Mafia. The Detective always sees you as innocent.",
        "tip": "You are the cleanest lie at the table. Use it.",
    },
    "doctor": {
        "title": "🩺 Moon Doctor",
        "goal": "Keep the town alive and eliminate the shadows.",
        "ability": (
            f"Protect one player each night. "
            f"Cannot protect the same player two nights in a row. "
            f"You may protect yourself, but only a limited number of times."
        ),
        "tip": "Protect smart players, not the loudest ones.",
    },
    "detective": {
        "title": "🕵️ Truth Seeker",
        "goal": "Find the shadows before they control the village.",
        "ability": "Investigate one player every night. The Crimson Monarch always appears innocent.",
        "tip": "Truth is power, but revealing it too early gets you killed.",
    },
    "bodyguard": {
        "title": "🛡 Silent Guardian",
        "goal": "Protect the town from the shadows.",
        "ability": "Guard one player each night. If that player is attacked, you die instead of them.",
        "tip": "Sometimes the strongest move is sacrifice.",
    },
    "mayor": {
        "title": "👑 Crowned Voice",
        "goal": "Use your influence to help the town eliminate Mafia.",
        "ability": "Your vote counts as 2 during town voting.",
        "tip": "People will follow your voice. Do not waste it.",
    },
    "jester": {
        "title": "🤡 Laughing Curse",
        "goal": "Get yourself voted out during the day.",
        "ability": "If the town executes you by vote, you win alone.",
        "tip": "Look suspicious, but not fake. That is the art.",
    },
    "cupid": {
        "title": "❤️ Fate Binder",
        "goal": "Bind two souls and create chaos through love.",
        "ability": "On Night 1 only — bind two lovers. If one dies, the other dies of heartbreak too.",
        "tip": "Love can be protection. Love can also be a weapon.",
    },
    "vigilante": {
        "title": "🔫 Midnight Gunner",
        "goal": "Help the town by shooting suspicious players at night.",
        "ability": "Shoot one player each night.",
        "tip": "A wrong shot can destroy the town faster than Mafia ever could.",
    },
    "witch": {
        "title": "🧙 Velvet Witch",
        "goal": "Survive and bend the night with your potions.",
        "ability": "You have one save potion and one kill potion for the entire game. Use each only once.",
        "tip": "Use both potions only when the table is worth changing.",
    },
    "silencer": {
        "title": "🎭 Silence Broker",
        "goal": "Help the shadows by removing a voice from the day.",
        "ability": "Silence one player each night. They cannot speak during the next discussion phase.",
        "tip": "Silence the clever ones, not just the loud.",
    },
    "trickster": {
        "title": "🃏 Fate Trickster",
        "goal": "Twist the vote chaos in your favor.",
        "ability": "Once per game, during voting, you can secretly swap the top 2 vote counts.",
        "tip": "The smartest lie is the one nobody notices.",
    },
    "medium": {
        "title": "👻 Grave Whisperer",
        "goal": "Listen to the dead and guide the living.",
        "ability": "You receive death reports each night and hear the last words of those who die.",
        "tip": "The dead know things the living missed.",
    },
    "undertaker": {
        "title": "⚰️ Soul Keeper",
        "goal": "Help the town by learning the truth from the dead.",
        "ability": "When anyone dies, you privately learn their role.",
        "tip": "Your knowledge is dangerous. Share it carefully.",
    },
    "arsonist": {
        "title": "🔥 Flame Gambler",
        "goal": "Play your own dangerous game — mark players, then ignite them all.",
        "ability": "Each night you can mark a player OR ignite all marked players at once.",
        "tip": "Patience makes the fire beautiful.",
    },
    "villager": {
        "title": "👤 Lost Citizen",
        "goal": "Find and eliminate all shadows from the village.",
        "ability": "No night power. Discuss, observe, vote, and survive.",
        "tip": "Even without powers, your vote can change fate.",
    },
}


def role_guide(role: str) -> str:
    data = ROLE_GUIDES.get(role, ROLE_GUIDES["villager"])

    return (
        "<blockquote>🎭 <b>Your Secret Role</b></blockquote>\n\n"
        f"<b>{data['title']}</b>\n\n"
        f"🎯 <b>Goal:</b>\n{data['goal']}\n\n"
        f"✨ <b>Ability:</b>\n{data['ability']}\n\n"
        f"♠️ <b>Yumeko's Tip:</b>\n<i>❝ {data['tip']} ♡ ❞</i>"
    )


# ──────────────────────────────────────────────
#  Static Pages
# ──────────────────────────────────────────────

def rules_text() -> str:
    return (
        "<blockquote>🎭 <b>Yumeko Mafia — Rules</b></blockquote>\n\n"
        "<i>❝ Everyone smiles. Someone is lying. Trust is the first thing to die. ♡ ❞</i>\n\n"
        "<b>Game Flow</b>\n"
        "🌙 <b>Night</b> — Secret roles act via private DM.\n"
        "☀️ <b>Day</b> — Players discuss who seems suspicious.\n"
        "🗳 <b>Voting</b> — Everyone votes using buttons.\n\n"
        "<b>Win Conditions</b>\n"
        "🔪 <b>Mafia</b> wins when Mafia equals or outnumbers town.\n"
        "🏡 <b>Town</b> wins when all Mafia are eliminated.\n"
        "🤡 <b>Jester</b> wins alone if voted out by the town.\n\n"
        "<b>Special Rules</b>\n"
        "🩺 Doctor cannot protect the same player two nights in a row.\n"
        "👑 Mayor's vote counts as 2.\n"
        "❤️ If one lover dies, the other dies from heartbreak.\n"
        "🛡 Bodyguard dies instead of the player they guard.\n"
        "🕶 Godfather always appears innocent to the Detective.\n\n"
        "<i>Use /mafia to begin a new game.</i>"
    )


def lobby_text(game: dict) -> str:
    advanced = ""
    if len(game["players"]) >= 8:
        advanced = "\n✨ <b>Advanced roles may appear tonight.</b>"

    return (
        "<blockquote>🎭 <b>Yumeko's Mafia Table</b></blockquote>\n\n"
        "<i>❝ Ahahaha~ welcome, darling.\n"
        "Tonight trust is a gamble, lies are currency,\n"
        "and someone at this table will not survive. ♡ ❞</i>\n\n"
        f"🎴 <b>Host:</b> {game['host_name']}\n"
        f"👥 <b>Players:</b> <code>{len(game['players'])}/{MAX_PLAYERS}</code>\n"
        f"⏳ <b>Starts In:</b> <code>{JOIN_TIME}s</code>"
        f"{advanced}\n\n"
        "━━━━━━━━━━━━━━\n"
        "🪑 <b>Seated Players</b>\n\n"
        f"{format_players(game)}\n"
        "━━━━━━━━━━━━━━\n\n"
        "🎲 <i>Tap below to take your seat before fate begins.</i>"
    )


def join_countdown_text(seconds: int) -> str:
    return (
        "<blockquote>⏳ <b>Mafia Lobby Closing</b></blockquote>\n\n"
        f"<i>❝ {seconds} seconds left. Sit at the table before fate begins. ♡ ❞</i>"
    )


def joined_text(name: str, count: int) -> str:
    return (
        "<blockquote>🎭 <b>Player Joined</b></blockquote>\n\n"
        f"<b>{name}</b> joined Mafia.\n\n"
        f"👥 Players now: <b>{count}</b>"
    )


def not_enough_text(game: dict) -> str:
    return (
        "<blockquote>😔 <b>Mafia Cancelled</b></blockquote>\n\n"
        f"Only <b>{len(game['players'])}</b> player(s) joined.\n"
        f"Minimum required: <b>{MIN_PLAYERS}</b>\n\n"
        "<i>Start a new game when more players are ready.</i>"
    )


# ──────────────────────────────────────────────
#  Night Phase
# ──────────────────────────────────────────────

def night_group_text(game: dict) -> str:
    return (
        f"<blockquote>🌙 <b>Night {game['day']}</b></blockquote>\n\n"
        "<i>❝ The village sleeps. The dangerous ones do not. ♡ ❞</i>\n\n"
        "All secret roles — check your private messages now.\n\n"
        f"⏳ Night lasts: <b>{NIGHT_TIME}s</b>\n\n"
        "<blockquote>👥 <b>Alive Players</b></blockquote>\n"
        f"{format_alive(game)}"
    )


def no_dm_text(name: str) -> str:
    return (
        f"⚠️ Could not send a DM to <b>{name}</b>.\n"
        "They must start the bot in private first: @YumekoBot"
    )


# ──────────────────────────────────────────────
#  Night Action DMs
# ──────────────────────────────────────────────

def mafia_action_dm(game: dict) -> str:
    mafia_names = [
        p["name"]
        for p in game["players"].values()
        if p["role"] in ("mafia", "godfather")
    ]

    return (
        "<blockquote>🔪 <b>Mafia Night</b></blockquote>\n\n"
        "<i>❝ Choose your victim carefully. The village will wake up asking questions. ♡ ❞</i>\n\n"
        f"👥 <b>Your Team:</b> {', '.join(mafia_names)}\n\n"
        "Tap a player below to select tonight's victim."
    )


def doctor_action_dm() -> str:
    return (
        "<blockquote>🩺 <b>Doctor Night</b></blockquote>\n\n"
        "<i>❝ One correct protection can ruin the perfect murder. ♡ ❞</i>\n\n"
        "Choose one player to protect tonight.\n\n"
        "<i>You cannot protect the same person two nights in a row.</i>"
    )


def detective_action_dm() -> str:
    return (
        "<blockquote>🕵️ <b>Detective Night</b></blockquote>\n\n"
        "<i>❝ Truth is dangerous when you are the only one holding it. ♡ ❞</i>\n\n"
        "Choose one player to investigate."
    )


def bodyguard_action_dm() -> str:
    return (
        "<blockquote>🛡 <b>Bodyguard Night</b></blockquote>\n\n"
        "<i>❝ A brave shield can become tomorrow's body. ♡ ❞</i>\n\n"
        "Choose one player to guard tonight.\n\n"
        "<i>If they are attacked, you die instead.</i>"
    )


def cupid_action_dm() -> str:
    return (
        "<blockquote>❤️ <b>Cupid Night 1</b></blockquote>\n\n"
        "<i>❝ Love is just another gamble, darling. ♡ ❞</i>\n\n"
        "Choose the <b>first</b> lover.\n\n"
        "<i>If either lover dies, the other dies from heartbreak.</i>"
    )


def villager_night_dm(role: str) -> str:
    return (
        f"{role_guide(role)}\n\n"
        "<blockquote>🌙 <b>Night</b></blockquote>\n\n"
        "You have no night action. Rest and wait for sunrise.\n\n"
        "<i>Use the day phase to observe and guide your team.</i>"
    )


def action_saved_text(action: str) -> str:
    return (
        "<blockquote>✅ <b>Action Recorded</b></blockquote>\n\n"
        f"{action}\n\n"
        "<i>❝ Yumeko has written it into fate. ♡ ❞</i>"
    )


def detective_result_text(target_name: str, is_mafia: bool) -> str:
    verdict = "🔪 <b>Mafia</b>" if is_mafia else "🏡 <b>Not Mafia</b>"
    return (
        "<blockquote>🕵️ <b>Investigation Result</b></blockquote>\n\n"
        f"<b>{target_name}</b> is {verdict}."
    )


def cupid_second_text(first_name: str) -> str:
    return (
        "<blockquote>❤️ <b>Cupid — Second Choice</b></blockquote>\n\n"
        f"First lover: <b>{first_name}</b>\n\n"
        "Now choose the second lover."
    )


# ──────────────────────────────────────────────
#  Day Phase
# ──────────────────────────────────────────────

def discussion_text(game: dict, result: dict) -> str:
    lines = []

    if result.get("saved"):
        lines.append("🩺 The Moon Doctor's protection was perfect — someone survived the night.")

    if result.get("witch_saved"):
        lines.append("🧙 The Velvet Witch used her save potion. Death was delayed.")

    if result.get("guarded"):
        lines.append("🛡 The Silent Guardian stepped in front of danger.")

    if result.get("bodyguard_dead"):
        lines.append(
            f"💀 <b>{result['bodyguard_dead']['name']}</b> "
            f"({role_name(result['bodyguard_dead']['role'])}) died protecting someone."
        )

    if result.get("killed"):
        lines.append(
            f"💀 <b>{result['killed']['name']}</b> "
            f"({role_name(result['killed']['role'])}) was found dead after the night."
        )

    if result.get("vigilante_killed"):
        lines.append(
            f"🔫 <b>{result['vigilante_killed']['name']}</b> "
            f"({role_name(result['vigilante_killed']['role'])}) was shot by the Midnight Gunner."
        )

    if result.get("witch_killed"):
        lines.append(
            f"🩸 <b>{result['witch_killed']['name']}</b> "
            f"({role_name(result['witch_killed']['role'])}) was poisoned by the Velvet Witch."
        )

    if result.get("arson_killed"):
        names = "\n".join(
            f"🔥 <b>{p['name']}</b> ({role_name(p['role'])})"
            for p in result["arson_killed"]
        )
        lines.append(
            "<blockquote>🔥 <b>The Flame Gambler Ignited The Table</b></blockquote>\n\n"
            "<i>❝ The village woke up to smoke, screams, and ashes. ♡ ❞</i>\n\n"
            f"{names}"
        )

    if result.get("lover_dead"):
        lines.append(
            f"💔 <b>{result['lover_dead']['name']}</b> "
            f"({role_name(result['lover_dead']['role'])}) died from heartbreak."
        )

    if not lines:
        lines.append("🌙 Nobody died tonight. Somehow, the silence survived.")

    silenced_id = game.get("night_actions", {}).get("silenced")
    silenced_text = ""

    if silenced_id and silenced_id in game["players"]:
        silenced_name = game["players"][silenced_id]["name"]
        silenced_text = (
            f"\n\n🎭 <b>Silenced:</b> "
            f'<a href="tg://user?id={silenced_id}">{silenced_name}</a>\n'
            f"<i>They cannot speak during this day phase.</i>"
        )

    return (
        f"<blockquote>☀️ <b>Day {game['day']} Begins</b></blockquote>\n\n"
        + "\n".join(lines)
        + "\n\n"
        f"📝 <b>Death Note:</b>\n<i>❝ {result.get('note', 'The night kept its secret.')} ❞</i>"
        + silenced_text
        + "\n\n"
        f"💬 Discussion time: <b>{DISCUSSION_TIME}s</b>\n\n"
        "<blockquote>👥 <b>Alive Players</b></blockquote>\n"
        f"{format_alive(game)}"
    )


# ──────────────────────────────────────────────
#  Voting Phase
# ──────────────────────────────────────────────

def voting_text(game: dict) -> str:
    return (
        "<blockquote>🗳 <b>Town Voting</b></blockquote>\n\n"
        "<i>❝ Point your finger carefully. One vote can bury the innocent. ♡ ❞</i>\n\n"
        f"⏳ Voting time: <b>{VOTE_TIME}s</b>\n\n"
        "Tap a name below to cast your vote."
    )


def vote_recorded_text(target_name: str) -> str:
    return f"🗳 Vote cast for <b>{target_name}</b>."


def vote_result_text(game: dict, result: dict) -> str:
    if not result:
        return "<blockquote>⚖️ <b>Vote Result</b></blockquote>\n\nNo result."

    if result.get("jester_win"):
        eliminated = result.get("eliminated", {}) or {}
        return (
            "<blockquote>🤡 <b>Jester Victory</b></blockquote>\n\n"
            f"<b>{eliminated.get('name', 'Someone')}</b> was voted out.\n\n"
            "<i>❝ The Laughing Curse played you all perfectly. ♡ ❞</i>\n\n"
            "The Jester wins alone."
        )

    if result.get("skip"):
        main = "⚖️ The village chose to skip the vote. Nobody was eliminated."
    elif result.get("tie"):
        main = "⚖️ The vote ended in a tie. Nobody was eliminated."
    elif result.get("eliminated"):
        e = result["eliminated"]
        main = (
            f"💀 <b>{e['name']}</b> was eliminated by the village.\n"
            f"Role revealed: {role_name(e['role'])}"
        )
    else:
        main = "Nobody was eliminated."

    if result.get("lover_dead"):
        ld = result["lover_dead"]
        main += (
            f"\n\n💔 <b>{ld['name']}</b> ({role_name(ld['role'])}) "
            f"died from heartbreak."
        )

    return (
        "<blockquote>⚖️ <b>Voting Result</b></blockquote>\n\n"
        f"{main}"
    )


# ──────────────────────────────────────────────
#  Game Over
# ──────────────────────────────────────────────

def winner_text(game: dict, winner: str, mvp: dict | None = None) -> str:
    if winner == "mafia":
        title = "🔪 Mafia Victory"
        desc = "The shadows have taken the town. Darkness wins."
    elif winner == "town":
        title = "🏡 Town Victory"
        desc = "The village survived the lies. Light wins."
    else:
        title = "🤡 Jester Victory"
        desc = "Chaos smiled and won alone. Nobody saw it coming."

    if winner == "jester":
        reward = (
            f"🤡 Jester: +<b>{JESTER_COINS}</b> coins | +<b>{JESTER_XP}</b> XP\n"
            f"📉 Others: +<b>{LOSE_XP}</b> XP"
        )
    else:
        reward = (
            f"🏆 Winners: +<b>{WIN_COINS}</b> coins | +<b>{WIN_XP}</b> XP\n"
            f"📉 Others: +<b>{LOSE_XP}</b> XP"
        )

    mvp_text = ""
    if mvp:
        mvp_text = (
            "\n\n<blockquote>🏆 <b>MVP Of The Match</b></blockquote>\n"
            f"👑 <b>{mvp['name']}</b>\n"
            f"🎭 Role: <b>{role_name(mvp['role'])}</b>\n"
            "💰 Bonus: +<b>50</b> Coins\n"
            "✨ Bonus: +<b>50</b> XP"
        )

    return (
        f"<blockquote>🏆 <b>{title}</b></blockquote>\n\n"
        f"<i>❝ {desc} ♡ ❞</i>\n\n"
        f"{reward}"
        f"{mvp_text}\n\n"
        "<blockquote>🎭 <b>Final Roles</b></blockquote>\n"
        f"{format_roles(game)}"
    )