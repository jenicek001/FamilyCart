# This file ensures that all models are imported when 'app.models' is imported.
# This is crucial for Alembic to detect all models for autogeneration.

from .user import User
from .category import Category
from .shopping_list import ShoppingList
from .item import Item
from .unit import Unit

__all__ = [
    "User",
    "Category",
    "ShoppingList",
    "Item",
    "Unit",
]
