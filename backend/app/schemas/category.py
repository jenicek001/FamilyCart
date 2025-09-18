from typing import Dict, Optional

from pydantic import BaseModel, ConfigDict


class CategoryBase(BaseModel):
    name: str
    icon_name: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    name: Optional[str] = None


class CategoryInDBBase(CategoryBase):
    id: int
    translations: Optional[Dict[str, str]] = None
    model_config = ConfigDict(from_attributes=True)


class Category(CategoryInDBBase):
    pass
