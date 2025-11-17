from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
admin_ids_str = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(x.strip()) for x in admin_ids_str.split(",") if x.strip()] if admin_ids_str else []
MAIN_ADMIN_ID = int(os.getenv("MAIN_ADMIN_ID"))
SUPPORT_BOT = os.getenv("SUPPORT_BOT", "plaza_support_BOT")
WEBAPP_URL = os.getenv("WEBAPP_URL")

START_BALANCE = 225
