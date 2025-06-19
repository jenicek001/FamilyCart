# This file ensures that all models are imported when 'app.models' is imported.
# This is crucial for Alembic to detect all models for autogeneration.

from .category import Category, CategoryTranslation
from .item import Item
from .shopping_list import ShoppingList, UserShoppingListLink
from .user import User

__all__ = [
    "User",
    "ShoppingList",
    "UserShoppingListLink",
    "Item",
    "Category",
    "CategoryTranslation",
]
