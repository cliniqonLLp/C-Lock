from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.db.base import Base


class SharedCredential(Base):
    __tablename__ = "shared_credentials"

    id = Column(Integer, primary_key=True, index=True)

    label = Column(String, nullable=False)

  
    domains_encrypted = Column(Text, nullable=False)

    
    username_encrypted = Column(Text, nullable=False)
    password_encrypted = Column(Text, nullable=False)

    created_by_user_id = Column(Integer, ForeignKey("users.id"))

    status = Column(String, default="active")  # active / disabled

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())