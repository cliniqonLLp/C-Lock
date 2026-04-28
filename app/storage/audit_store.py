import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parents[2]
AUDIT_FILE = BASE_DIR / "data" / "audit_logs.json"


def load_audit_logs():
    try:
        with open(AUDIT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def append_audit_log(user_id: int, vault_id: int, domain_used: str, action: str, status: str):
    logs = load_audit_logs()
    next_id = (logs[-1]["id"] + 1) if logs else 1

    logs.append({
        "id": next_id,
        "user_id": user_id,
        "vault_id": vault_id,
        "domain_used": domain_used,
        "action": action,
        "status": status,
        "timestamp": datetime.utcnow().isoformat()
    })

    with open(AUDIT_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2)