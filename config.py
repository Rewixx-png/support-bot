import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", 0))
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "bot.db")

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)