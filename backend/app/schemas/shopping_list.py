import uuid
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.user import UserRead

class ShoppingListBase(BaseModel):
    name: str
    description: Optional[str] = None

class ShoppingListCreate(ShoppingListBase):
    pass

class ShoppingListUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    
    def dict(self, *args, **kwargs):
        kwargs.pop("exclude_unset", None)
        return super().dict(*args, exclude_unset=True, **kwargs)

class ShoppingListRead(ShoppingListBase):
    id: int
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    items: list = []  # Default to empty list if no items
    members: List[UserRead] = []  # List of users who have access to this list

    class Config:
        from_attributes = True
        # Serialize UUIDs as strings to avoid JSON serialization issues
        json_encoders = {
            uuid.UUID: str,
            datetime: lambda v: v.isoformat() if v else None
        }
