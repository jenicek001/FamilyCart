# This file resolves forward references in Pydantic models
from app.schemas.shopping_list import ShoppingListRead
from app.schemas.item import ItemRead

# Update forward references
ShoppingListRead.model_rebuild()
