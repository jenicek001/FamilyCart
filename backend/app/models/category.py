\
import uuid
from typing import TYPE_CHECKING, List, Optional

from app.db.base import Base
from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer, String,
                        UniqueConstraint)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

if TYPE_CHECKING:
    from .item import Item
    from .user import User  # If categories are user-specific or have owners

class Category(Base):
    __tablename__ = "category"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True) # Default name, e.g., "Fruits"
    
    # If categories are user-specific or system-wide
    # owner_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("user.id"), nullable=True, index=True) # Null for system categories
    # owner: Mapped[Optional["User"]] = relationship()

    # For ordering categories (e.g., in a dropdown or a management UI)
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    
    # Default language for the category name if using translations
    default_lang_code: Mapped[str] = mapped_column(String(5), default="en", nullable=False)

    # Relationships
    items: Mapped[List["Item"]] = relationship(back_populates="category")
    
    translations: Mapped[List["CategoryTranslation"]] = relationship(
        back_populates="category",
        cascade="all, delete-orphan"
    )

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # __table_args__ = (
    #     # Ensure category names are unique per owner, or globally if owner_id is null
    #     # This requires careful handling if owner_id can be NULL.
    #     # UniqueConstraint('owner_id', 'name', name='_user_category_name_uc'), 
    # )


    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name='{self.name}')>"


class CategoryTranslation(Base):
    __tablename__ = "category_translation"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("category.id", ondelete="CASCADE"), nullable=False, index=True)
    lang_code: Mapped[str] = mapped_column(String(5), nullable=False, index=True) # e.g., "en", "es", "de"
    translated_name: Mapped[str] = mapped_column(String(100), nullable=False)

    category: Mapped["Category"] = relationship(back_populates="translations")

    __table_args__ = (
        UniqueConstraint('category_id', 'lang_code', name='_category_lang_uc'),
    )

    def __repr__(self) -> str:
        return f"<CategoryTranslation(id={self.id}, category_id='{self.category_id}', lang='{self.lang_code}', name='{self.translated_name}')>"
