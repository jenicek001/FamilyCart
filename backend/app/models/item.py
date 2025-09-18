from datetime import datetime
from typing import Optional

from sqlalchemy import (Boolean, DateTime, ForeignKey, Integer, Numeric,
                        String, Text)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base
from ..utils.timezone import utc_now
from .category import Category
from .shopping_list import ShoppingList
from .unit import Unit
from .user import User


class Item(Base):
    """Item model for shopping list items."""

    __tablename__ = "item"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    standardized_name: Mapped[str | None] = mapped_column(String(100))
    translations: Mapped[dict | None] = mapped_column(JSONB)

    # Legacy quantity field (to be removed after migration)
    quantity: Mapped[str | None] = mapped_column(String(50))

    # New structured quantity fields
    quantity_value: Mapped[float | None] = mapped_column(Numeric(10, 3))
    quantity_unit_id: Mapped[str | None] = mapped_column(
        String(20), ForeignKey("unit.id")
    )
    quantity_display_text: Mapped[str | None] = mapped_column(String(100))

    comment: Mapped[str | None] = mapped_column(Text)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    icon_name: Mapped[str | None] = mapped_column(String(50))  # For Lucide icon name

    # Use timezone-aware DateTime columns
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )

    # Relationships
    shopping_list_id: Mapped[int] = mapped_column(ForeignKey("shopping_list.id"))
    shopping_list: Mapped["ShoppingList"] = relationship(back_populates="items")

    owner_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    owner: Mapped["User"] = relationship(foreign_keys=[owner_id])

    last_modified_by_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    last_modified_by: Mapped["User"] = relationship(foreign_keys=[last_modified_by_id])

    category_id: Mapped[int | None] = mapped_column(ForeignKey("category.id"))
    category: Mapped[Optional["Category"]] = relationship(back_populates="items")

    # Relationship to quantity unit
    unit: Mapped[Optional["Unit"]] = relationship("Unit")

    def __str__(self) -> str:
        return f"{self.name} ({self.quantity})"
