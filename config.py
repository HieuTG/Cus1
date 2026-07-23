import os
from dotenv import load_dotenv

# Nạp các biến môi trường từ file .env
load_dotenv()

# Token Bot
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")

# ID của các Role (tự động chuyển sang kiểu int)
VERIFY_MACE_ROLE_ID = int(os.getenv("VERIFY_MACE_ROLE_ID", 0))
TESTER_ROLE_ID = int(os.getenv("TESTER_ROLE_ID", 0))

TIER_ROLES = {
    "HT1": int(os.getenv("ROLE_HT1", 0)),
    "LT1": int(os.getenv("ROLE_LT1", 0)),
    "HT2": int(os.getenv("ROLE_HT2", 0)),
    "LT2": int(os.getenv("ROLE_LT2", 0)),
    "HT3": int(os.getenv("ROLE_HT3", 0)),
    "LT3": int(os.getenv("ROLE_LT3", 0)),
    "HT4": int(os.getenv("ROLE_HT4", 0)),
    "LT4": int(os.getenv("ROLE_LT4", 0)),
    "HT5": int(os.getenv("ROLE_HT5", 0)),
    "LT5": int(os.getenv("ROLE_LT5", 0)),
}