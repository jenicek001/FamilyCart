import uuid
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# A simple schema for Category to be used in ItemRead
class CategoryRead(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

# Shared properties
class ItemBase(BaseModel):
    name: str
    quantity: Optional[str] = None
    description: Optional[str] = None

# Properties to receive on item creation
class ItemCreate(ItemBase):
    category_name: Optional[str] = None # The backend will handle resolving this to a category_id

# Properties to receive on item update
class ItemUpdate(BaseModel):
    name: Optional[str] = None
    quantity: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    category_id: Optional[int] = None
    icon_name: Optional[str] = None

# Properties to return to client
class ItemRead(ItemBase):
    id: int
    shopping_list_id: int
    owner_id: uuid.UUID
    is_completed: bool
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryRead] = None
    icon_name: Optional[str] = None

    class Config:
        from_attributes = True
