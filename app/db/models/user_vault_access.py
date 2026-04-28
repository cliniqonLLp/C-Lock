from sqlalchemy import Integer, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class UserVaultAccess(Base):
    __tablename__ = "user_vault_access"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)                                  
    vault_item_id: Mapped[int] = mapped_column(ForeignKey("vault_items.id"), nullable=False)
    access_type: Mapped[str] = mapped_column(String(50), default="use")