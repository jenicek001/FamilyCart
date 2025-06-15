from sqlalchemy import String, ForeignKey, Boolean, Integer
from sqlalchemy.orm import Mapped, relationship, mapped_column
from typing import TYPE_CHECKING
from datetime import datetime
import uuid

from ..db.base import Base

if TYPE_CHECKING:
    from .shopping_list import ShoppingList

class Item(Base):
    """Item model for shopping list items."""
    
    __tablename__ = "item"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit: Mapped[str | None] = mapped_column(String(20), nullable=True)
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_purchased: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    # Shopping list relationship
    shopping_list_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("shoppinglist.id"))
    shopping_list: Mapped["ShoppingList"] = relationship(back_populates="items")

    def __str__(self) -> str:
        return f"{self.name} ({self.quantity} {self.unit if self.unit else ''})"
