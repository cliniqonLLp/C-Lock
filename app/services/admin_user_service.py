from sqlalchemy.orm import Session
from app.db.models.user import User
from app.core.security import hash_password


def create_user(db: Session, name: str, email: str, password: str, role: str):
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        return {"success": False, "message": "User already exists"}

    user = User(
        name=name,
        email=email,
        password_hash=hash_password(password),
        role=role,
        is_active=True
    )

    db.add(user)
    db.commit()

    return {"success": True, "message": "User created"}