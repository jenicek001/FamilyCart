from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


class CRUDCategory(CRUDBase[Category, CategoryCreate, CategoryUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[Category]:
        return db.query(Category).filter(Category.name == name).first()

    def create(self, db: Session, *, obj_in: CategoryCreate) -> Category:
        db_obj = Category(
            name=obj_in.name,
            icon_name=obj_in.icon_name,
            translations=obj_in.translations or {}
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


category = CRUDCategory(Category)
