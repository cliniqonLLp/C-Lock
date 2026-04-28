from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func

from app.db.base import Base


class FillToken(Base):
    __tablename__ = "fill_tokens"

    id = Column(Integer, primary_key=True, index=True)

    token = Column(String, unique=True, index=True, nullable=False)

    username = Column(String, nullable=False)
    password = Column(String, nullable=False)

    expires_at = Column(DateTime, nullable=False)

    is_used = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())