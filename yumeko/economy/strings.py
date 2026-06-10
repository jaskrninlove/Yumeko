# ==========================================================
#  Yumeko Games Bot
#  Copyright (c) 2026 Jass
# ==========================================================

def balance_text(name: str, data: dict):
    return (
        f"<blockquote>💰 <b>Yumeko Wallet</b></blockquote>\n\n"
        f"👤 Player: <b>{name}</b>\n\n"
        f"💰 Coins: <b>{data['coins']}</b>\n"
        f"✨ XP: <b>{data['xp']}</b>\n\n"
        f"<i>❝ Yumeko counts every coin you dared to earn. ♡ ❞</i>"
    )


def work_text(job: str, coins: int, xp: int):
    return (
        f"<blockquote>💼 <b>Work Complete</b></blockquote>\n\n"
        f"🎭 Job: <b>{job}</b>\n\n"
        f"💰 Earned: +<b>{coins}</b> coins\n"
        f"✨ XP: +<b>{xp}</b>\n\n"
        f"<i>❝ Hard work is cute... but gambling is faster. ♡ ❞</i>"
    )


def crime_success_text(coins: int, xp: int):
    return (
        f"<blockquote>🦹 <b>Crime Successful</b></blockquote>\n\n"
        f"<i>❝ Ahahaha~ risky hands, lucky pockets. ♡ ❞</i>\n\n"
        f"💰 Stolen: +<b>{coins}</b> coins\n"
        f"✨ XP: +<b>{xp}</b>"
    )


def crime_fail_text(lost: int, xp: int):
    return (
        f"<blockquote>🚔 <b>Crime Failed</b></blockquote>\n\n"
        f"<i>❝ Oh my~ you got caught, darling. ❞</i>\n\n"
        f"💸 Lost: -<b>{lost}</b> coins\n"
        f"✨ XP: +<b>{xp}</b>"
    )


def beg_text(coins: int, xp: int):
    return (
        f"<blockquote>🥺 <b>Begging Result</b></blockquote>\n\n"
        f"<i>❝ Yumeko felt a little generous today. Just a little. ♡ ❞</i>\n\n"
        f"💰 Received: +<b>{coins}</b> coins\n"
        f"✨ XP: +<b>{xp}</b>"
    )


def cooldown_text(command: str, remaining: str):
    return (
        f"<blockquote>⏳ <b>Cooldown</b></blockquote>\n\n"
        f"You already used <code>/{command}</code>.\n\n"
        f"Come back in: <b>{remaining}</b>\n\n"
        f"<i>❝ Patience, darling. Greed needs timing. ♡ ❞</i>"
    )


def pay_usage_text():
    return (
        f"<blockquote>💸 <b>Pay Usage</b></blockquote>\n\n"
        f"Reply to someone with:\n"
        f"<code>/pay 500</code>"
    )


def pay_success_text(sender: str, target: str, amount: int):
    return (
        f"<blockquote>💸 <b>Payment Sent</b></blockquote>\n\n"
        f"<b>{sender}</b> gave <b>{amount}</b> coins to <b>{target}</b>.\n\n"
        f"<i>❝ Money moves beautifully when hearts are reckless. ♡ ❞</i>"
    )


def not_enough_coins_text():
    return (
        f"<blockquote>💸 <b>Not Enough Coins</b></blockquote>\n\n"
        f"<i>❝ You cannot spend coins you do not have, darling. ❞</i>"
    )