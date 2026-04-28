from app.db.session import SessionLocal
from app.db.models.user import User
from app.core.security import hash_password

db = SessionLocal()

existing = db.query(User).filter(User.email == "admin@cliniqon.com").first()

if existing:
    print("Admin already exists")
else:
    admin = User(
        name="Admin",
        email="admin@cliniqon.com",
        password_hash=hash_password("admin123"),
        role="admin",
        is_active=True
    )

    db.add(admin)
    db.commit()
    print("Admin created")

db.close()