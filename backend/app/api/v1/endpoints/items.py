import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_session, set_session_context
from app.core.fastapi_users import current_user
from app.models import Category, Item, ShoppingList, User
from app.schemas.item import ItemCreate, ItemCreateStandalone, ItemRead, ItemUpdate
from app.services.ai_service import ai_service
from app.services.websocket_service import websocket_service

router = APIRouter()
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


async def get_or_create_category(
    name: Optional[str], session: AsyncSession
) -> Optional[Category]:
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


@router.post("/", response_model=ItemRead)
async def create_item(
    *,
    session: AsyncSession = Depends(get_session),
    item_in: ItemCreateStandalone,
    current_user: User = Depends(current_user),
):
    """
    Create a new item in a shopping list.
    """
    # Validate access to the shopping list (owner or shared member)
    shopping_list = await get_shopping_list_by_id(
        list_id=item_in.shopping_list_id, session=session, current_user=current_user
    )

    category_name = item_in.category_name
    if not category_name:
        category_name = await ai_service.suggest_category(item_in.name, session)

    category = await get_or_create_category(category_name, session)

    icon_name = item_in.icon_name
    if not icon_name:
        cat_name_for_icon = category_name if category_name else "Uncategorized"
        icon_name = await ai_service.suggest_icon(item_in.name, cat_name_for_icon)

    # Standardize and translate item name
    standardization_result = await ai_service.standardize_and_translate_item_name(
        item_in.name
    )
    standardized_name = standardization_result.get("standardized_name")
    translations = standardization_result.get("translations")

    db_item = Item(
        name=item_in.name,
        standardized_name=standardized_name,
        translations=translations,
        quantity=item_in.quantity,
        comment=item_in.comment,
        shopping_list_id=item_in.shopping_list_id,
        owner_id=current_user.id,
        last_modified_by_id=current_user.id,
        category_id=category.id if category else None,
        icon_name=icon_name,
        # New structured quantity fields
        quantity_value=item_in.quantity_value,
        quantity_unit_id=item_in.quantity_unit_id,
        quantity_display_text=item_in.quantity_display_text,
    )
    session.add(db_item)
    await session.commit()
    await session.refresh(
        db_item, attribute_names=["category", "owner", "last_modified_by"]
    )
    return db_item


@router.get("/{item_id}", response_model=ItemRead)
async def read_item(
    item_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(current_user),
):
    """
    Get an item by ID.
    """
    result = await session.execute(
        select(Item)
        .where(Item.id == item_id)
        .options(
            selectinload(Item.shopping_list).selectinload(ShoppingList.shared_with),
            selectinload(Item.category),
            selectinload(Item.owner),
            selectinload(Item.last_modified_by),
        )
    )
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Check if user has permission to view items in this shopping list
    # Allow both owner and shared users to view items
    if (
        item.shopping_list.owner_id != current_user.id
        and current_user not in item.shopping_list.shared_with
    ):
        raise HTTPException(status_code=403, detail="Not authorized to view this item")

    return item


@router.get("/list/{list_id}", response_model=List[ItemRead])
async def read_items_from_list(
    list_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(current_user),
):
    """
    Get all items from a specific shopping list.
    """
    # Check if the shopping list exists and if user has access to it
    result = await session.execute(
        select(ShoppingList)
        .where(ShoppingList.id == list_id)
        .options(selectinload(ShoppingList.shared_with))
    )
    shopping_list = result.scalars().first()
    if not shopping_list:
        raise HTTPException(status_code=404, detail="Shopping list not found")

    # Check if user has permission to view items in this shopping list
    # Allow both owner and shared users to view items
    if (
        shopping_list.owner_id != current_user.id
        and current_user not in shopping_list.shared_with
    ):
        raise HTTPException(
            status_code=403, detail="Not authorized to view items in this list"
        )
    # Eagerly load category for all items
    result = await session.execute(
        select(Item)
        .where(Item.shopping_list_id == list_id)
        .options(
            selectinload(Item.category),
            selectinload(Item.shopping_list),
            selectinload(Item.owner),
            selectinload(Item.last_modified_by),
        )
    )
    items = result.scalars().all()
    return items


@router.put("/{item_id}", response_model=ItemRead)
async def update_item(
    *,
    session: AsyncSession = Depends(get_session),
    item_id: int,
    item_in: ItemUpdate,
    current_user: User = Depends(current_user),
    _session_context: str = Depends(set_session_context),
):
    """
    Update an item.
    """
    # Capture user ID early to avoid async context issues
    current_user_id = str(current_user.id)
    # Eagerly load shopping_list relationship including shared_with
    result = await session.execute(
        select(Item)
        .where(Item.id == item_id)
        .options(
            selectinload(Item.shopping_list).selectinload(ShoppingList.shared_with),
            selectinload(Item.category),
            selectinload(Item.owner),
            selectinload(Item.last_modified_by),
        )
    )
    db_item = result.scalars().first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Check if user has permission to update items in this shopping list
    # Allow both owner and shared users to update items
    if (
        db_item.shopping_list.owner_id != current_user.id
        and current_user not in db_item.shopping_list.shared_with
    ):
        raise HTTPException(
            status_code=403, detail="Not authorized to update this item"
        )

    # Store original values for audit logging
    original_is_completed = db_item.is_completed

    update_data = item_in.dict(exclude_unset=True)

    # If item name is updated, suggest new category and icon if not provided
    if "name" in update_data:
        category_name_for_icon = "Uncategorized"

        # Suggest category if not provided
        if "category_id" not in update_data:
            suggested_category_name = await ai_service.suggest_category(
                update_data["name"], session
            )
            category = await get_or_create_category(suggested_category_name, session)
            if category:
                db_item.category_id = category.id
            category_name_for_icon = suggested_category_name
        elif db_item.category:
            # Category is not being updated, but we need its name for icon suggestion
            category_name_for_icon = db_item.category.name

        # Suggest icon if not provided
        if "icon_name" not in update_data:
            new_icon_name = await ai_service.suggest_icon(
                update_data["name"], category_name_for_icon
            )
            db_item.icon_name = new_icon_name

        # Standardize and translate the new item name
        standardization_result = await ai_service.standardize_and_translate_item_name(
            update_data["name"]
        )
        db_item.standardized_name = standardization_result.get("standardized_name")
        db_item.translations = standardization_result.get("translations")

    for key, value in update_data.items():
        setattr(db_item, key, value)

    # Update last_modified_by when item is updated
    db_item.last_modified_by_id = current_user.id

    # Audit logging for item completion status changes
    if "is_completed" in update_data and original_is_completed != db_item.is_completed:
        status_text = "completed" if db_item.is_completed else "uncompleted"
        logger.info(
            f"Item status changed - User: {current_user.email} | "
            f"Item ID: {db_item.id} | Item: '{db_item.name}' | "
            f"Status: {status_text} | List: '{db_item.shopping_list.name}'"
        )

    session.add(db_item)
    await session.commit()
    await session.refresh(
        db_item, attribute_names=["category", "owner", "last_modified_by"]
    )

    # Send real-time notification to list members
    try:
        from app.schemas.item import ItemRead

        item_data = ItemRead.model_validate(db_item, from_attributes=True).model_dump(
            mode="json"
        )
        await websocket_service.notify_item_updated(
            list_id=db_item.shopping_list_id,
            item_data=item_data,
            user_id=current_user_id,
        )
    except Exception as e:
        logger.error(f"Failed to send WebSocket notification for item update: {e}")
        logger.exception("Full exception details:")

    return db_item


@router.delete("/{item_id}", response_model=dict)
async def delete_item(
    *,
    session: AsyncSession = Depends(get_session),
    item_id: int,
    current_user: User = Depends(current_user),
    _session_context: str = Depends(set_session_context),
):
    """
    Delete an item.
    """
    # Capture user ID early to avoid async context issues
    current_user_id = str(current_user.id)
    # Eagerly load shopping_list relationship including shared_with
    result = await session.execute(
        select(Item)
        .where(Item.id == item_id)
        .options(
            selectinload(Item.shopping_list).selectinload(ShoppingList.shared_with),
            selectinload(Item.owner),
            selectinload(Item.last_modified_by),
        )
    )
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Check if user has permission to delete items in this shopping list
    # Allow both owner and shared users to delete items
    if (
        item.shopping_list.owner_id != current_user.id
        and current_user not in item.shopping_list.shared_with
    ):
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this item"
        )

    # Store list_id before deletion for WebSocket notification
    list_id = item.shopping_list_id
    item_id_for_notification = item.id

    await session.delete(item)
    await session.commit()

    # Send real-time notification to list members
    try:
        await websocket_service.notify_item_deleted(
            list_id=list_id, item_id=item_id_for_notification, user_id=current_user_id
        )
    except Exception as e:
        logger.error(f"Failed to send WebSocket notification for item deletion: {e}")

    return {"message": "Item deleted successfully"}
