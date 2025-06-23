from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.dependencies import get_current_user
from app.models import User, Item, ShoppingList, Category
from app.schemas.item import ItemRead, ItemCreate, ItemUpdate
from app.api.deps import get_session

router = APIRouter()

async def get_or_create_category(name: Optional[str], session: AsyncSession) -> Optional[Category]:
    """Find an existing category or create a new one."""
    if not name:
        return None
    
    result = await session.execute(select(Category).where(Category.name == name.strip()))
    category = result.scalars().first()
    
    if not category:
        category = Category(name=name.strip())
        session.add(category)
        await session.commit()
        await session.refresh(category)
        
    return category

@router.post("/", response_model=ItemRead)
async def create_item(
    *,
    session: AsyncSession = Depends(get_session),
    item_in: ItemCreate,
    current_user: User = Depends(get_current_user),
):
    """
    Create a new item in a shopping list.
    """
    result = await session.execute(select(ShoppingList).where(ShoppingList.id == item_in.shopping_list_id))
    shopping_list = result.scalars().first()
    
    if not shopping_list:
        raise HTTPException(status_code=404, detail="Shopping list not found")
    
    if shopping_list.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to add items to this list")

    category = await get_or_create_category(item_in.category_name, session)

    db_item = Item(
        name=item_in.name,
        quantity=item_in.quantity,
        description=item_in.description,
        shopping_list_id=item_in.shopping_list_id,
        owner_id=current_user.id,
        category_id=category.id if category else None
    )
    session.add(db_item)
    await session.commit()
    await session.refresh(db_item)
    return db_item

@router.get("/{item_id}", response_model=ItemRead)
async def read_item(
    item_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Get an item by ID.
    """
    result = await session.execute(select(Item).where(Item.id == item_id))
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    if item.shopping_list.owner_id != current_user.id:
         raise HTTPException(status_code=403, detail="Not authorized to view this item")

    return item

@router.put("/{item_id}", response_model=ItemRead)
async def update_item(
    *,
    session: AsyncSession = Depends(get_session),
    item_id: int,
    item_in: ItemUpdate,
    current_user: User = Depends(get_current_user),
):
    """
    Update an item.
    """
    result = await session.execute(select(Item).where(Item.id == item_id))
    db_item = result.scalars().first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    if db_item.shopping_list.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this item")

    update_data = item_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
    
    session.add(db_item)
    await session.commit()
    await session.refresh(db_item)
    return db_item

@router.delete("/{item_id}", response_model=dict)
async def delete_item(
    *,
    session: AsyncSession = Depends(get_session),
    item_id: int,
    current_user: User = Depends(get_current_user),
):
    """
    Delete an item.
    """
    result = await session.execute(select(Item).where(Item.id == item_id))
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if item.shopping_list.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this item")

    await session.delete(item)
    await session.commit()
    return {"message": "Item deleted successfully"}

