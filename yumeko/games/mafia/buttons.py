# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
# ==========================================================

from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from yumeko.games.mafia.game import available_targets


def split_buttons(items, per_row=2):
    rows = []
    temp = []

    for item in items:
        temp.append(item)

        if len(temp) == per_row:
            rows.append(temp)
            temp = []

    if temp:
        rows.append(temp)

    return rows


# ----------------------------------------------------------
# MAFIA KILL
# ----------------------------------------------------------

def mafia_kill_buttons(game, mafia_id):
    buttons = []

    for player in available_targets(
        game,
        actor_id=mafia_id,
        include_self=False,
    ):
        if player["role"] == "mafia":
            continue

        buttons.append(
            InlineKeyboardButton(
                player["name"],
                callback_data=f"mf_kill_{player['id']}",
            )
        )

    return InlineKeyboardMarkup(
        split_buttons(buttons)
    )


# ----------------------------------------------------------
# DOCTOR SAVE
# ----------------------------------------------------------

def doctor_save_buttons(game, doctor_id):
    buttons = []

    for player in available_targets(
        game,
        actor_id=doctor_id,
        include_self=True,
    ):
        buttons.append(
            InlineKeyboardButton(
                player["name"],
                callback_data=f"mf_save_{player['id']}",
            )
        )

    return InlineKeyboardMarkup(
        split_buttons(buttons)
    )


# ----------------------------------------------------------
# DETECTIVE CHECK
# ----------------------------------------------------------

def detective_buttons(game, detective_id):
    buttons = []

    for player in available_targets(
        game,
        actor_id=detective_id,
        include_self=False,
    ):
        buttons.append(
            InlineKeyboardButton(
                player["name"],
                callback_data=f"mf_check_{player['id']}",
            )
        )

    return InlineKeyboardMarkup(
        split_buttons(buttons)
    )


# ----------------------------------------------------------
# BODYGUARD
# ----------------------------------------------------------

def bodyguard_buttons(game, guard_id):
    buttons = []

    for player in available_targets(
        game,
        actor_id=guard_id,
        include_self=False,
    ):
        buttons.append(
            InlineKeyboardButton(
                player["name"],
                callback_data=f"mf_guard_{player['id']}",
            )
        )

    return InlineKeyboardMarkup(
        split_buttons(buttons)
    )


# ----------------------------------------------------------
# CUPID
# ----------------------------------------------------------

def cupid_first_pick_buttons(game):
    buttons = []

    for player in available_targets(game):
        buttons.append(
            InlineKeyboardButton(
                player["name"],
                callback_data=f"mf_cupid1_{player['id']}",
            )
        )

    return InlineKeyboardMarkup(
        split_buttons(buttons)
    )


def cupid_second_pick_buttons(game, first_id):
    buttons = []

    for player in available_targets(game):
        if player["id"] == first_id:
            continue

        buttons.append(
            InlineKeyboardButton(
                player["name"],
                callback_data=f"mf_cupid2_{first_id}_{player['id']}",
            )
        )

    return InlineKeyboardMarkup(
        split_buttons(buttons)
    )


# ----------------------------------------------------------
# DAY VOTING
# ----------------------------------------------------------

def voting_buttons(game):
    buttons = []

    for player in available_targets(game):
        buttons.append(
            InlineKeyboardButton(
                player["name"],
                callback_data=f"mf_vote_{player['id']}",
            )
        )

    rows = split_buttons(buttons)

    rows.append(
        [
            InlineKeyboardButton(
                "⚖️ Skip Vote",
                callback_data="mf_vote_skip",
            )
        ]
    )

    return InlineKeyboardMarkup(rows)


# ----------------------------------------------------------
# SPECTATOR PANEL
# ----------------------------------------------------------

def spectator_buttons():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🎭 View Roles",
                    callback_data="mf_roles",
                )
            ]
        ]
    )


# ----------------------------------------------------------
# GAME PANEL
# ----------------------------------------------------------

def game_panel_buttons():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "👥 Players",
                    callback_data="mf_players",
                ),
                InlineKeyboardButton(
                    "📊 Status",
                    callback_data="mf_status",
                ),
            ]
        ]
    )

# ----------------------------------------------------------
# VIGILANTE
# ----------------------------------------------------------

def vigilante_buttons(game, vigilante_id):
    buttons = []

    for player in available_targets(
        game,
        actor_id=vigilante_id,
        include_self=False,
    ):
        buttons.append(
            InlineKeyboardButton(
                player["name"],
                callback_data=f"mf_vigi_{player['id']}",
            )
        )

    return InlineKeyboardMarkup(split_buttons(buttons))


# ----------------------------------------------------------
# WITCH
# ----------------------------------------------------------

def witch_buttons(game, witch_id):
    player = game["players"].get(witch_id, {})

    save_used = player.get("witch_save_used", False)
    kill_used = player.get("witch_kill_used", False)

    rows = []

    if not kill_used:
        rows.append(
            [
                InlineKeyboardButton(
                    "🩸 Use Kill Potion",
                    callback_data="mf_witch_kill_menu",
                )
            ]
        )

    if not save_used:
        rows.append(
            [
                InlineKeyboardButton(
                    "🧪 Use Save Potion",
                    callback_data="mf_witch_save_menu",
                )
            ]
        )

    if not rows:
        rows.append(
            [
                InlineKeyboardButton(
                    "🧙 Magic Exhausted",
                    callback_data="mf_witch_empty",
                )
            ]
        )

    return InlineKeyboardMarkup(rows)

def witch_kill_buttons(game, witch_id):
    buttons = []

    for player in available_targets(game, actor_id=witch_id, include_self=False):
        buttons.append(
            InlineKeyboardButton(
                player["name"],
                callback_data=f"mf_witchkill_{player['id']}",
            )
        )

    return InlineKeyboardMarkup(split_buttons(buttons))


def witch_save_buttons(game, witch_id):
    buttons = []

    for player in available_targets(game, actor_id=witch_id, include_self=True):
        buttons.append(
            InlineKeyboardButton(
                player["name"],
                callback_data=f"mf_witchsave_{player['id']}",
            )
        )

    return InlineKeyboardMarkup(split_buttons(buttons))

# ----------------------------------------------------------
# SILENCER
# ----------------------------------------------------------

def silencer_buttons(game, silencer_id):
    buttons = []

    for player in available_targets(
        game,
        actor_id=silencer_id,
        include_self=False,
    ):
        buttons.append(
            InlineKeyboardButton(
                player["name"],
                callback_data=f"mf_silence_{player['id']}",
            )
        )

    return InlineKeyboardMarkup(split_buttons(buttons))


# ----------------------------------------------------------
# ARSONIST
# ----------------------------------------------------------

def arsonist_buttons(game, arsonist_id):
    rows = []

    marked = game.get("arsonist_marks", [])

    mark_buttons = []

    for player in available_targets(
        game,
        actor_id=arsonist_id,
        include_self=False,
    ):
        prefix = "✅ Marked" if player["id"] in marked else "🔥 Mark"

        mark_buttons.append(
            InlineKeyboardButton(
                f"{prefix} {player['name']}",
                callback_data=f"mf_arsonmark_{player['id']}",
            )
        )

    rows.extend(split_buttons(mark_buttons, per_row=1))

    if marked:
        rows.append(
            [
                InlineKeyboardButton(
                    f"🔥 Ignite {len(marked)} Marked Player(s)",
                    callback_data="mf_arsonignite",
                )
            ]
        )

    return InlineKeyboardMarkup(rows)

def trickster_vote_button():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🃏 Twist The Vote",
                    callback_data="mf_trickster_twist",
                )
            ]
        ]
    )