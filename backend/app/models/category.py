import uuid
from typing import TYPE_CHECKING, List

from app.db.base import Base
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, relationship, mapped_column

if TYPE_CHECKING:
    from .item import Item

class Category(Base):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)

    # Relationships
    items: Mapped[List["Item"]] = relationship(back_populates="category")

    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name='{self.name}')>"
