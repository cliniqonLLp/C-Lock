import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
USERS_FILE = BASE_DIR / "data" / "users.json"


def load_users():
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_user_by_email(email: str):
    for user in load_users():
        if user["email"].lower() == email.lower():
            return user
    return None


def get_user_by_id(user_id: int):
    for user in load_users():
        if user["id"] == user_id:
            return user
    return None