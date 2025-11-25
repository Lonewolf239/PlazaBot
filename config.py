from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
admin_ids_str = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(x.strip()) for x in admin_ids_str.split(",") if x.strip()] if admin_ids_str else []
MAIN_ADMIN_ID = int(os.getenv("MAIN_ADMIN_ID"))
promoter_ids_str = os.getenv("PROMOTER_IDS")
PROMOTER_IDS = [int(x.strip()) for x in promoter_ids_str.split(",") if x.strip()] if promoter_ids_str else []
SUPPORT_BOT = os.getenv("SUPPORT_BOT", "plaza_support_BOT")
WEBAPP_URL = os.getenv("WEBAPP_URL")
SECRET_KEY_STR = os.getenv("SECRET_KEY_STR")
START_BALANCE = 225
