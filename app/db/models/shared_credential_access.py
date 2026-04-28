from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.sql import func

from app.db.base import Base


class SharedCredentialAccess(Base):
    __tablename__ = "shared_credential_access"

    id = Column(Integer, primary_key=True, index=True)

    shared_credential_id = Column(
        Integer, ForeignKey("shared_credentials.id"), nullable=False
    )

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    access_type = Column(String, default="use")  # use / owner

    created_at = Column(DateTime(timezone=True), server_default=func.now())