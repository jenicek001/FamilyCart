"""Helper functions for shopping list operations."""

import logging
from typing import List

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import User
from app.models.category import Category
from app.models.item import Item
from app.models.shopping_list import ShoppingList
from app.schemas.item import ItemRead
from app.schemas.shopping_list import ShoppingListRead
from app.schemas.user import UserRead

logger = logging.getLogger(__name__)


async def get_shopping_list_by_id(
    list_id: int,
    session: AsyncSession,
    current_user: User,
):
    """
    Helper function to retrieve a ShoppingList by ID,
    ensuring current_user is owner or shared member.
    """
    result = await session.execute(
        select(ShoppingList)
        .where(ShoppingList.id == list_id)
        .options(
            selectinload(ShoppingList.shared_with),
            selectinload(ShoppingList.items),
            selectinload(ShoppingList.owner),
        )
    )
    shopping_list = result.scalars().first()
    if not shopping_list:
        raise HTTPException(status_code=404, detail="Shopping list not found")
    if (
        shopping_list.owner_id != current_user.id
        and current_user not in shopping_list.shared_with
    ):
        raise HTTPException(
            status_code=403, detail="Not authorized to access this list"
        )
    return shopping_list


async def get_or_create_category(name: str, session: AsyncSession) -> Category:
    """Find an existing category or create a new one."""
    if not name:
        return None

    result = await session.execute(
        select(Category).where(Category.name == name.strip())
    )
    category = result.scalars().first()

    if not category:
        category = Category(name=name.strip())
        session.add(category)
        await session.commit()
        await session.refresh(category)

    return category


async def build_shopping_list_response(
    shopping_list, session: AsyncSession, current_user: User
) -> ShoppingListRead:
    """
    Helper function to safely build a ShoppingListRead response from a SQLAlchemy model.
    Ensures all relationships are properly loaded and converted to Pydantic models.
    """
    # Eagerly load all relationships
    result = await session.execute(
        select(ShoppingList)
        .where(ShoppingList.id == shopping_list.id)
        .options(
            selectinload(ShoppingList.items).selectinload(Item.category),
            selectinload(ShoppingList.items).selectinload(Item.owner),
            selectinload(ShoppingList.items).selectinload(Item.last_modified_by),
            selectinload(ShoppingList.shared_with),
            selectinload(ShoppingList.owner),
        )
    )
    fresh_shopping_list = result.scalars().first()

    # Convert items to Pydantic models
    items = []
    if fresh_shopping_list.items:
        sorted_items = sort_items_by_category(fresh_shopping_list.items)
        items = [ItemRead.model_validate(i, from_attributes=True) for i in sorted_items]

    # Convert members to Pydantic models
    members = [
        UserRead.model_validate(u, from_attributes=True)
        for u in fresh_shopping_list.shared_with
    ]
    if fresh_shopping_list.owner_id != current_user.id:
        members.append(
            UserRead.model_validate(fresh_shopping_list.owner, from_attributes=True)
        )

    # Build and return Pydantic model
    return ShoppingListRead(
        id=fresh_shopping_list.id,
        name=fresh_shopping_list.name,
        description=fresh_shopping_list.description,
        owner_id=fresh_shopping_list.owner_id,
        created_at=fresh_shopping_list.created_at,
        updated_at=fresh_shopping_list.updated_at,
        items=items,
        members=members,
    )


def sort_items_by_category(items: List[Item]) -> List[Item]:
    """
    Sort items by category, then by completion status, then by name.
    Items with categories come first, sorted alphabetically by category name.
    Items without categories come last.
    Within each category, uncompleted items come first.
    """

    def sort_key(item: Item):
        # Primary sort: category name (None/empty comes last)
        category_name = item.category.name if item.category else "zzz_uncategorized"
        # Secondary sort: completion status (False comes before True)
        completion_status = item.is_completed
        # Tertiary sort: item name
        item_name = item.name.lower()

        return (category_name, completion_status, item_name)

    return sorted(items, key=sort_key)