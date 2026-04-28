from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class VaultDomain(Base):
    __tablename__ = "vault_domains"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    vault_item_id: Mapped[int] = mapped_column(ForeignKey("vault_items.id"), nullable=False)
    domain: Mapped[str] = mapped_column(String(255), nullable=False, index=True)