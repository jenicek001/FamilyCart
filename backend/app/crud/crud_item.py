from typing import Any, Dict, List, Optional, Union

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate


class CRUDItem(CRUDBase[Item, ItemCreate, ItemUpdate]):
    def create_with_owner_and_list(
        self, db: Session, *, obj_in: ItemCreate, owner_id: int, shopping_list_id: int
    ) -> Item:
        db_obj = self.model(
            **obj_in.model_dump(exclude_unset=True),
            owner_id=owner_id,
            last_modified_by_id=owner_id,  # Set last_modified_by_id on creation
            shopping_list_id=shopping_list_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: Item,
        obj_in: Union[ItemUpdate, Dict[str, Any]],
        last_modified_by_id: int,
    ) -> Item:
        # Use the base update method first
        updated_obj = super().update(db, db_obj=db_obj, obj_in=obj_in)
        # Set the last modified by id
        updated_obj.last_modified_by_id = last_modified_by_id
        db.add(updated_obj)
        db.commit()
        db.refresh(updated_obj)
        return updated_obj

    def get_multi_by_shopping_list(
        self, db: Session, *, shopping_list_id: int, skip: int = 0, limit: int = 100
    ) -> List[Item]:
        return (
            db.query(self.model)
            .filter(Item.shopping_list_id == shopping_list_id)
            .offset(skip)
            .limit(limit)
            .all()
        )


item = CRUDItem(Item)
