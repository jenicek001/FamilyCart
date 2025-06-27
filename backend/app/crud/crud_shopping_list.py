from typing import List, Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.shopping_list import ShoppingList
from app.schemas.shopping_list import ShoppingListCreate, ShoppingListUpdate


class CRUDShoppingList(CRUDBase[ShoppingList, ShoppingListCreate, ShoppingListUpdate]):
    def get_multi_by_owner(
        self, db: Session, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[ShoppingList]:
        return (
            db.query(self.model)
            .filter(ShoppingList.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
            .all()
        )


shopping_list = CRUDShoppingList(ShoppingList)
