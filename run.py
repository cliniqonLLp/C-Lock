from app.db.base import Base
from app.db.session import engine
import app.db.models  # important: loads all models

Base.metadata.create_all(bind=engine)

print("Tables created successfully")