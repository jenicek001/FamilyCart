import uuid
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# A simple schema for Category to be used in ItemRead
class CategoryRead(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

# A simple schema for User to be used in ItemRead (to avoid circular imports)
class UserBasic(BaseModel):
    id: uuid.UUID
    email: str
    nickname: Optional[str] = None

    class Config:
        from_attributes = True

# Shared properties
class ItemBase(BaseModel):
    name: str
    quantity: Optional[str] = None
    description: Optional[str] = None
    standardized_name: Optional[str] = None
    translations: Optional[dict[str, str]] = None

# Properties to receive on item creation
class ItemCreate(ItemBase):
    category_name: Optional[str] = None # The backend will handle resolving this to a category_id
    icon_name: Optional[str] = None

# Properties to receive on item creation via standalone endpoint (requires shopping_list_id)
class ItemCreateStandalone(ItemCreate):
    shopping_list_id: int

# Properties to receive on item update
class ItemUpdate(BaseModel):
    name: Optional[str] = None
    quantity: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    category_id: Optional[int] = None
    icon_name: Optional[str] = None
    standardized_name: Optional[str] = None
    translations: Optional[dict[str, str]] = None

# Properties to return to client
class ItemRead(ItemBase):
    id: int
    shopping_list_id: int
    owner_id: uuid.UUID
    owner: Optional[UserBasic] = None
    last_modified_by_id: uuid.UUID
    last_modified_by: Optional[UserBasic] = None
    is_completed: bool
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryRead] = None
    icon_name: Optional[str] = None
    standardized_name: Optional[str] = None
    translations: Optional[dict[str, str]] = None

    class Config:
        from_attributes = True
