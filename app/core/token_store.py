from datetime import datetime, timedelta
from app.config import settings

SESSION_TOKENS = {}
FILL_TOKENS = {}


def create_session_token(user_id: int) -> str:
    from app.core.security import generate_token
    token = generate_token()
    SESSION_TOKENS[token] = {
        "user_id": user_id,
        "expires_at": datetime.utcnow() + timedelta(hours=8)
    }
    return token


def get_user_id_from_session(token: str):
    record = SESSION_TOKENS.get(token)
    if not record:
        return None
    if record["expires_at"] < datetime.utcnow():
        SESSION_TOKENS.pop(token, None)
        return None
    return record["user_id"]


def create_fill_token(user_id: int, vault_id: int, domain: str) -> str:
    from app.core.security import generate_token
    token = generate_token()
    FILL_TOKENS[token] = {
        "user_id": user_id,
        "vault_id": vault_id,
        "domain": domain,
        "expires_at": datetime.utcnow() + timedelta(seconds=settings.FILL_TOKEN_TTL_SECONDS),
        "used": False
    }
    return token


def consume_fill_token(token: str):
    record = FILL_TOKENS.get(token)
    if not record:
        return None
    if record["used"]:
        return None
    if record["expires_at"] < datetime.utcnow():
        FILL_TOKENS.pop(token, None)
        return None
    record["used"] = True
    return record