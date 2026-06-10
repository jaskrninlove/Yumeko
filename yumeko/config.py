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

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    API_ID = int(os.getenv("API_ID", "0"))
    API_HASH = os.getenv("API_HASH", "")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")

    OWNER_ID = int(os.getenv("OWNER_ID", "0"))
    LOGGER_CHAT_ID = int(os.getenv("LOGGER_CHAT_ID", "0"))

    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

    SUPPORT_GROUP = os.getenv("SUPPORT_GROUP", "https://t.me/yumekoarcade")
    UPDATE_CHANNEL = os.getenv("UPDATE_CHANNEL", "https://t.me/yumekoorg")
    BOT_USERNAME = os.getenv("BOT_USERNAME", "YumekoGamesBot")

    START_IMAGE = "yumeko/assets/images/start.jpg"

    MAFIA_NIGHT_GIF = "CgACAgQAAyEFAAToglSJAAILUGogKQGuRpTJug8rr6D4BUap52SdAAKMBQACGJ30Uh3hsQv4UA4yHgQ"
    MAFIA_DAY_GIF = "CgACAgQAAyEFAAToglSJAAILU2ogKQF85FfjGzxXe9wOaGHCAAFQ1QACwgcAAmJR9FCNaaVoqQJvYB4E"
    MAFIA_VOTING_GIF = "CgACAgQAAyEFAAToglSJAAILTmogKQHCZ8aLqlcVReVf6rlTdG6qAALkBwACunwEUDojYNMFsQovHgQ"
    MAFIA_DEATH_GIF = "CgACAgQAAyEFAAToglSJAAILb2ogKhEnZQPWxCq73cmZHYTe_gnCAALXBwACHmK8UVl50-CyfDmiHgQ"
    MAFIA_WIN_GIF = "CgACAgQAAyEFAAToglSJAAILVGogKQHgYf97th-xN0ocEJULAAFt_wACZAcAAu7HpFCDRsTsWogYHx4E"
    MAFIA_JESTER_GIF = "CgACAgQAAyEFAAToglSJAAILUmogKQEweyE8v-_mkLkz9yeh_PvuAAKVBAACi-G8UwvadXEXJ6FPHgQ"

    SKETCH_START_MEDIA = None
    SKETCH_TURN_MEDIA = None
    SKETCH_WIN_MEDIA = None
    SKETCH_DRAW_TIME = 120
    DRAW_WEBAPP_URL = "https://yumeko-canvas.vercel.app/"
    
    SNL_WEBAPP_URL  = "https://yumeko-snl.vercel.app"
    SNL_START_GIF   = None
    SNL_SNAKE_GIF   = None
    SNL_LADDER_GIF  = None
    SNL_WIN_GIF     = None
    SNL_YUMEKO_GIF  = None
    SNL_SABOTAGE_GIF= None
    
    RACING_WEBAPP_URL = "https://yumeko-racing.vercel.app/"

config = Config()