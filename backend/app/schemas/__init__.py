# This file resolves forward references in Pydantic models
from app.schemas.item import ItemRead
from app.schemas.shopping_list import ShoppingListRead

# Update forward references
ShoppingListRead.model_rebuild()
