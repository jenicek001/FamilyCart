from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Assuming a schema for Category exists in .category
# If not, you might need to define a simple one here.
class Category(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

# Shared properties
class ItemBase(BaseModel):
    name: str
    quantity: Optional[str] = None
    description: Optional[str] = None

# Properties to receive on item creation
# We receive category_name and let the backend handle finding/creating the category ID.
class ItemCreate(ItemBase):
    shopping_list_id: int
    category_name: Optional[str] = None

# Properties to receive on item update
class ItemUpdate(BaseModel):
    name: Optional[str] = None
    quantity: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    category_id: Optional[int] = None
    icon_name: Optional[str] = None

# Properties to return to client
class Item(ItemBase):
    id: int
    shopping_list_id: int
    is_completed: bool
    created_at: datetime
    updated_at: datetime
    category: Optional[Category] = None
    icon_name: Optional[str] = None
    owner_id: int

    class Config:
        orm_mode = True
