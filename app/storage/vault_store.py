import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
VAULT_FILE = BASE_DIR / "data" / "vault_items.json"


def load_vault_items():
    with open(VAULT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_vault_item_by_id(vault_id: int):
    for item in load_vault_items():
        if item["id"] == vault_id:
            return item
    return None