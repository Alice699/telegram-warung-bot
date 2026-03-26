import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "ISI_TOKEN_BOT_KAMU_DI_SINI")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(","))) if os.getenv("ADMIN_IDS") else []
WARUNG_NAME = os.getenv("WARUNG_NAME", "Warung Digital 🍜")
