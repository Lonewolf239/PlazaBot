from pathlib import Path
from dotenv import load_dotenv
import os

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

TEST = True
CRYPTOPAY_API_TOKEN = os.getenv("CRYPTOPAY_API_TOKEN")
CRYPTOPAY_TEST_API_TOKEN = os.getenv("CRYPTOPAY_TEST_API_TOKEN")
CRYPTOPAY_WEBHOOK = os.getenv("CRYPTOPAY_WEBHOOK")
