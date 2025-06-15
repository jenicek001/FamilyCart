from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy import String, Boolean, ForeignKey
from typing import List, TYPE_CHECKING
from ..db.base import Base

if TYPE_CHECKING:
    from .shopping_list import ShoppingList

class User(SQLAlchemyBaseUserTableUUID, Base):
    """User model with additional fields for profile information and relationships."""
    
    # Profile information
    first_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    # Relationships
    shopping_lists: Mapped[List["ShoppingList"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan"
    )
    
    shared_lists: Mapped[List["ShoppingList"]] = relationship(
        secondary="user_shopping_list",
        back_populates="shared_with"
    )

    def __str__(self) -> str:
        """String representation of the user."""
        return f"{self.first_name} {self.last_name}" if self.first_name and self.last_name else self.email

# If you need a separate OAuthAccount table (fastapi-users usually handles this internally or via association table)
# class OAuthAccount(SQLAlchemyBaseOAuthAccountTableUUID, Base):
#     pass
