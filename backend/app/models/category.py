import uuid
from typing import TYPE_CHECKING, List

from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from .item import Item


class Category(Base):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True, index=True
    )
    icon_name: Mapped[str | None] = mapped_column(String(50))
    translations: Mapped[dict | None] = mapped_column(JSONB)

    # Relationships
    items: Mapped[List["Item"]] = relationship(back_populates="category")

    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name='{self.name}')>"
