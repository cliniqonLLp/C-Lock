from app.db.session import SessionLocal
from app.db.models.user import User
from app.core.security import hash_password

db = SessionLocal()

admin = User(
    name="Admin",
    email="admin@cliniqon.com",
    password_hash=hash_password("admin123"),
    role="admin",
    is_active=True
)

db.add(admin)
db.commit()
db.refresh(admin)

print("Admin created:", admin.email)
db.close()