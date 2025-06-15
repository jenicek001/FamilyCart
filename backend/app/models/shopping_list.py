from sqlalchemy import String, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, relationship, mapped_column
from typing import List, TYPE_CHECKING
from datetime import datetime
import uuid

from ..db.base import Base

if TYPE_CHECKING:
    from .user import User
    from .item import Item

# Association table for many-to-many relationship between users and shopping lists
user_shopping_list = Table(
    "user_shopping_list",
    Base.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("shopping_list_id", ForeignKey("shoppinglist.id"), primary_key=True),
)

class ShoppingList(Base):
    """Shopping list model with relationships to users and items."""
    
    __tablename__ = "shoppinglist"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    # Owner relationship
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"))
    owner: Mapped["User"] = relationship(back_populates="shopping_lists")

    # Users with whom the list is shared
    shared_with: Mapped[List["User"]] = relationship(
        secondary=user_shopping_list,
        back_populates="shared_lists"
    )

    # Items in the list
    items: Mapped[List["Item"]] = relationship(
        back_populates="shopping_list",
        cascade="all, delete-orphan"
    )

    def __str__(self) -> str:
        return self.name
