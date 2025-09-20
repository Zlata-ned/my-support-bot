import os
from dotenv import load_dotenv

load_dotenv()

bot_token = os.getenv("bot_token")
db_name = 'bot.db'