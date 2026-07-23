import json
import os

DATA_FILE = "data.json"

default_data = {
    "user_profiles": {},
    "waitlist": [],
    "queue_open": True,
    "ticket_category_id": None,
    "result_channel_id": None,
    "active_tests": [],
    "queue_opener_id": None,
    "queue_message_info": {"channel_id": None, "message_id": None}
}

def load():
    if not os.path.exists(DATA_FILE):
        return default_data

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Chuyển ID người dùng từ chuỗi (string) trong JSON về số (int)
            if "user_profiles" in data:
                data["user_profiles"] = {int(k): v for k, v in data["user_profiles"].items()}
            return data
    except Exception as e:
        print(f"⚠️ Lỗi đọc data.json: {e}")
        return default_data

def save():
    """Hàm này sẽ ghi toàn bộ biến hiện tại vào file data.json"""
    data = {
        "user_profiles": user_profiles,
        "waitlist": waitlist,
        "queue_open": queue_open,
        "ticket_category_id": ticket_category_id,
        "result_channel_id": result_channel_id,
        "active_tests": active_tests,
        "queue_opener_id": queue_opener_id,
        "queue_message_info": queue_message_info
    }
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"❌ Lỗi ghi file data.json: {e}")

# Tự động nạp dữ liệu khi import
_initial_data = load()
user_profiles = _initial_data.get("user_profiles", {})
waitlist = _initial_data.get("waitlist", [])
queue_open = _initial_data.get("queue_open", True)
ticket_category_id = _initial_data.get("ticket_category_id", None)
result_channel_id = _initial_data.get("result_channel_id", None)
active_tests = _initial_data.get("active_tests", [])
queue_opener_id = _initial_data.get("queue_opener_id", None)
queue_message_info = _initial_data.get("queue_message_info", {"channel_id": None, "message_id": None})