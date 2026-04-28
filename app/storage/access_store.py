import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
ACCESS_FILE = BASE_DIR / "data" / "access_map.json"


def load_access_map():
    with open(ACCESS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_vault_ids_for_user(user_id: int):
    return [
        item["vault_id"]
        for item in load_access_map()
        if item["user_id"] == user_id
    ]