import os

TOKEN = os.getenv("BOT_TOKEN")
ADMINS_ID = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))
