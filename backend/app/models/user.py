from typing import TYPE_CHECKING, List

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base

if TYPE_CHECKING:
    from .shopping_list import ShoppingList


class User(SQLAlchemyBaseUserTableUUID, Base):
    """User model with additional fields for profile information and relationships."""

    # Profile information
    first_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    nickname: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Relationships
    owned_shopping_lists: Mapped[List["ShoppingList"]] = relationship(
        foreign_keys="[ShoppingList.owner_id]",
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    shared_lists: Mapped[List["ShoppingList"]] = relationship(
        secondary="user_shopping_list", back_populates="shared_with"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}')>"

    @property
    def display_name(self) -> str:
        """Returns the user's display name (nickname if available, otherwise full name or email)."""
        if self.nickname:
            return self.nickname
        return self.full_name

    @property
    def full_name(self) -> str:
        """Returns the user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email


# If you need a separate OAuthAccount table (fastapi-users usually handles this internally or via association table)
# class OAuthAccount(SQLAlchemyBaseOAuthAccountTableUUID, Base):
#     pass
