from fastapi import Header, HTTPException, Depends, Cookie
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.db.session import SessionLocal
from app.db.models.session_token import SessionToken
from app.db.models.user import User


INACTIVITY_DAYS = 3


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    authorization: str = Header(default=""),
    session_token: str = Cookie(default=None),
    db: Session = Depends(get_db)
):
    if authorization.startswith("Bearer "):
        token_value = authorization.replace("Bearer ", "", 1).strip()
    elif session_token:
        token_value = session_token
    else:
        raise HTTPException(status_code=401, detail="Missing token")

    now = datetime.utcnow()

    session = (
        db.query(SessionToken)
        .filter(
            SessionToken.access_token == token_value,
            SessionToken.is_active == True
        )
        .first()
    )

    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")

    if session.access_expires_at < now:
        raise HTTPException(status_code=401, detail="Access token expired")

    if session.refresh_expires_at < now:
        session.is_active = False
        db.commit()
        raise HTTPException(status_code=401, detail="Session expired due to inactivity")

    session.last_activity_at = now
    session.refresh_expires_at = now + timedelta(days=INACTIVITY_DAYS)
    db.commit()

    user = db.query(User).filter(User.id == session.user_id, User.is_active == True).first()

    if not user:
        raise HTTPException(status_code=401, detail="User inactive")

    return user


def get_admin_user(user=Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user