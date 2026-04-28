from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.db.models.user import User
from app.db.models.session_token import SessionToken
from app.core.security import verify_password, generate_token


ACCESS_TOKEN_MINUTES = 30
INACTIVITY_DAYS = 3


def login_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return {"success": False, "message": "User not found"}

    if not user.is_active:
        return {"success": False, "message": "User inactive"}

    if not verify_password(password, user.password_hash):
        return {"success": False, "message": "Invalid password"}

    now = datetime.utcnow()

    access_token = generate_token()
    refresh_token = generate_token()

    session = SessionToken(
        user_id=user.id,
        access_token=access_token,
        refresh_token=refresh_token,
        is_active=True,
        access_expires_at=now + timedelta(minutes=ACCESS_TOKEN_MINUTES),
        refresh_expires_at=now + timedelta(days=INACTIVITY_DAYS),
        last_activity_at=now
    )

    db.add(session)
    db.commit()

    return {
        "success": True,
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "name": user.name,
        "email": user.email,
        "role": user.role
    }


def refresh_session(db: Session, refresh_token: str):
    now = datetime.utcnow()

    session = (
        db.query(SessionToken)
        .filter(
            SessionToken.refresh_token == refresh_token,
            SessionToken.is_active == True
        )
        .first()
    )

    if not session:
        return {"success": False, "message": "Invalid refresh token"}

    if session.refresh_expires_at < now:
        session.is_active = False
        db.commit()
        return {"success": False, "message": "Session expired due to inactivity"}

    new_access_token = generate_token()
    new_refresh_token = generate_token()

    session.access_token = new_access_token
    session.refresh_token = new_refresh_token
    session.access_expires_at = now + timedelta(minutes=ACCESS_TOKEN_MINUTES)
    session.refresh_expires_at = now + timedelta(days=INACTIVITY_DAYS)
    session.last_activity_at = now

    db.commit()

    return {
        "success": True,
        "access_token": new_access_token,
        "refresh_token": new_refresh_token
    }


def logout_user(db: Session, refresh_token: str):
    session = (
        db.query(SessionToken)
        .filter(SessionToken.refresh_token == refresh_token)
        .first()
    )

    if session:
        session.is_active = False
        db.commit()

    return {"success": True, "message": "Logged out"}