import uuid
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ShoppingListBase(BaseModel):
    name: str
    description: Optional[str] = None

class ShoppingListCreate(ShoppingListBase):
    pass

class ShoppingListUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class ShoppingListRead(ShoppingListBase):
    id: int
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
