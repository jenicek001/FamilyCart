from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.dependencies import get_current_user
from app.models import User
from app.models.shopping_list import ShoppingList
from app.schemas.shopping_list import ShoppingListRead, ShoppingListCreate
from app.api.deps import get_session

router = APIRouter()

@router.post("/", response_model=ShoppingListRead)
async def create_shopping_list(
    *,
    session: AsyncSession = Depends(get_session),
    list_in: ShoppingListCreate,
    current_user: User = Depends(get_current_user),
):
    """
    Create new shopping list.
    """
    # Create a new ShoppingList SQLAlchemy model instance
    db_list = ShoppingList(
        name=list_in.name,
        description=list_in.description,
        owner_id=current_user.id
    )
    session.add(db_list)
    await session.commit()
    await session.refresh(db_list)
    return db_list


@router.get("/", response_model=List[ShoppingListRead])
async def read_shopping_lists(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve user's shopping lists (owned and shared).
    """
    # In a real app, you'd also query lists where the user is a member.
    result = await session.execute(select(ShoppingList).where(ShoppingList.owner_id == current_user.id))
    lists = result.scalars().all()
    return lists

