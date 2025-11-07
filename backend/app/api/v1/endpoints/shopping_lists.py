import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_session, set_session_context
from app.core.fastapi_users import current_user
from app.models import User
from app.models.item import Item
from app.models.shopping_list import ShoppingList
from app.schemas.item import ItemCreate, ItemRead
from app.schemas.share import ShareRequest
from app.schemas.shopping_list import (
    ShoppingListCreate,
    ShoppingListRead,
    ShoppingListUpdate,
)
from app.schemas.user import UserRead

# Import extracted modules
from ..helpers import shopping_list_helpers as helpers
from ..services import shopping_list_services as services
from .item_ai_service import ItemAIProcessor
from .response_builders import ResponseBuilder
from .websocket_helpers import WebSocketNotifier

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=ShoppingListRead)
async def create_shopping_list(
    *,
    session: AsyncSession = Depends(get_session),
    list_in: ShoppingListCreate,
    current_user: User = Depends(current_user),
):
    """
    Create new shopping list.
    """
    db_list = ShoppingList(
        name=list_in.name, description=list_in.description, owner_id=current_user.id
    )
    session.add(db_list)
    await session.commit()
    await session.refresh(db_list)

    # Eagerly load owner and shared_with
    await session.refresh(db_list, attribute_names=["owner", "shared_with", "items"])

    from app.schemas.item import ItemRead
    from app.schemas.user import UserRead

    items = []
    # Members: shared_with + owner if not already included
    members = [
        UserRead.model_validate(u, from_attributes=True) for u in db_list.shared_with
    ]
    if db_list.owner_id:
        members.append(UserRead.model_validate(db_list.owner, from_attributes=True))

    return ShoppingListRead(
        id=db_list.id,
        name=db_list.name,
        description=db_list.description,
        owner_id=db_list.owner_id,
        created_at=db_list.created_at,
        updated_at=db_list.updated_at,
        items=items,
        members=members,
    )


@router.get("/", response_model=List[ShoppingListRead])
async def read_shopping_lists(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(current_user),
):
    """
    Retrieve user's shopping lists (owned and shared).
    """
    try:
        # Eagerly load items and shared_with for owned lists
        result = await session.execute(
            select(ShoppingList)
            .where(ShoppingList.owner_id == current_user.id)
            .options(
                selectinload(ShoppingList.items).selectinload(Item.category),
                selectinload(ShoppingList.items).selectinload(Item.owner),
                selectinload(ShoppingList.items).selectinload(Item.last_modified_by),
                selectinload(ShoppingList.shared_with),
            )
        )
        owned_lists = result.scalars().all()

        # Eagerly load items and shared_with for shared lists
        shared_ids_result = await session.execute(
            select(ShoppingList.id)
            .join(ShoppingList.shared_with)
            .where(User.id == current_user.id)
        )
        shared_ids = shared_ids_result.scalars().all()
        if shared_ids:
            shared_lists_result = await session.execute(
                select(ShoppingList)
                .where(ShoppingList.id.in_(shared_ids))
                .options(
                    selectinload(ShoppingList.items).selectinload(Item.category),
                    selectinload(ShoppingList.items).selectinload(Item.owner),
                    selectinload(ShoppingList.items).selectinload(
                        Item.last_modified_by
                    ),
                    selectinload(ShoppingList.shared_with),
                )
            )
            shared_lists = shared_lists_result.scalars().all()
        else:
            shared_lists = []

        lists = list(owned_lists) + list(shared_lists)
        # Use response builder for cleaner code
        return await ResponseBuilder.build_lists_response(lists, current_user)

    except Exception as e:
        print(f"Error in read_shopping_lists: {e}")
        raise


@router.get("/{list_id}", response_model=ShoppingListRead)
async def read_shopping_list(
    list_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(current_user),
):
    """
    Get a specific shopping list by ID.
    """
    # Get shopping list with permission check
    shopping_list = await helpers.get_shopping_list_by_id(
        list_id, session, current_user
    )

    # Use helper function to build proper Pydantic response
    # The helper will handle eager loading, sorting, and conversion to Pydantic models
    return await helpers.build_shopping_list_response(
        shopping_list, session, current_user
    )


@router.put("/{list_id}", response_model=ShoppingListRead)
async def update_shopping_list(
    list_id: int,
    list_in: ShoppingListUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(current_user),
    _session_context: str = Depends(set_session_context),
):
    """
    Update a shopping list details.
    """
    # Capture user ID early to avoid async context issues
    current_user_id = str(current_user.id)

    # Get shopping list with permission check
    shopping_list = await helpers.get_shopping_list_by_id(
        list_id, session, current_user
    )

    # Update list attributes
    update_data = list_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(shopping_list, key, value)

    await session.commit()
    await session.refresh(shopping_list)

    # Eagerly load relationships for response
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
    shopping_list = result.scalars().first()

    # Build Pydantic response with items and members
    items = (
        [ItemRead.model_validate(i, from_attributes=True) for i in shopping_list.items]
        if shopping_list.items
        else []
    )
    members = [
        UserRead.model_validate(u, from_attributes=True)
        for u in shopping_list.shared_with
    ]
    if shopping_list.owner_id != current_user.id:
        members.append(
            UserRead.model_validate(shopping_list.owner, from_attributes=True)
        )

    # Create the response object and explicitly set items and members
    list_read = ShoppingListRead.model_validate(shopping_list, from_attributes=True)
    list_read.items = items
    list_read.members = members

    # Send real-time notification to list members
    try:
        list_data = list_read.model_dump(mode="json")
        await WebSocketNotifier.notify_list_updated(
            list_id=list_id,
            list_data=list_data,
            user_id=current_user_id,
        )
    except Exception:
        logger.exception("Failed to send WebSocket list_updated notification")

    return list_read


@router.delete("/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shopping_list(
    list_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(current_user),
    _session_context: str = Depends(set_session_context),
):
    """
    Delete a shopping list.
    """
    # Capture user ID before any database operations to avoid async context issues
    user_id = str(current_user.id)

    # Get shopping list with permission check
    shopping_list = await helpers.get_shopping_list_by_id(
        list_id, session, current_user
    )
    await session.delete(shopping_list)
    await session.commit()

    # Notify via WebSocket
    try:
        await WebSocketNotifier.notify_list_deleted(
            list_id=list_id,
            user_id=user_id,
        )
    except Exception:
        logger.exception("Failed to send WebSocket list_deleted notification")


@router.post("/{list_id}/items", response_model=ItemRead)
async def create_item_for_list(
    list_id: int,
    item_in: ItemCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(current_user),
    _session_context: str = Depends(set_session_context),
):
    """
    Add an item to a specific shopping list.
    Uses AI to automatically categorize items and standardize names.
    """
    # Get shopping list with permission check
    shopping_list = await helpers.get_shopping_list_by_id(
        list_id, session, current_user
    )
    user_id = current_user.id
    # Capture all values immediately to avoid lazy loading issues during AI operations
    shopping_list_id = shopping_list.id

    # Extract all values from item_in to avoid any potential async context issues
    item_name = item_in.name
    item_quantity = item_in.quantity
    item_comment = item_in.comment
    item_category_name = item_in.category_name
    item_icon_name = getattr(item_in, "icon_name", None)
    item_quantity_value = item_in.quantity_value
    item_quantity_unit_id = item_in.quantity_unit_id
    item_quantity_display_text = item_in.quantity_display_text

    # Use AI to process the item
    category, standardized_name, translations, icon_name = (
        await ItemAIProcessor.process_item_with_ai(
            item_name, item_category_name, session
        )
    )

    # Create new item with AI-enhanced data
    db_item = Item(
        name=item_name,
        quantity=item_quantity,
        comment=item_comment,
        shopping_list_id=shopping_list_id,
        owner_id=user_id,
        last_modified_by_id=user_id,
        category_id=category.id if category else None,
        icon_name=icon_name or item_icon_name,
        standardized_name=standardized_name,
        translations=translations,
        # New structured quantity fields
        quantity_value=item_quantity_value,
        quantity_unit_id=item_quantity_unit_id,
        quantity_display_text=item_quantity_display_text,
    )

    session.add(db_item)
    await session.commit()
    await session.refresh(db_item)
    # Eagerly load relationships for response
    await session.refresh(db_item, attribute_names=["category", "owner"])

    # Send real-time notification to list members
    from app.schemas.item import ItemRead

    item_data = ItemRead.model_validate(db_item, from_attributes=True).model_dump(
        mode="json"
    )
    await WebSocketNotifier.notify_item_created(
        list_id=list_id, item_data=item_data, user_id=str(user_id)
    )

    return db_item


@router.get("/{list_id}/items", response_model=List[ItemRead])
async def read_items_from_list(
    list_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(current_user),
):
    """
    Get all items from a specific shopping list.
    """
    # Get shopping list with permission check
    shopping_list = await helpers.get_shopping_list_by_id(
        list_id, session, current_user
    )
    # Eagerly load category for all items
    result = await session.execute(
        select(Item)
        .where(Item.shopping_list_id == shopping_list.id)
        .options(
            selectinload(Item.category),
            selectinload(Item.shopping_list),
            selectinload(Item.owner),
        )
    )
    items = result.scalars().all()
    return items


@router.post("/{list_id}/share", response_model=ShoppingListRead)
async def share_shopping_list(
    list_id: int,
    share_data: ShareRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(current_user),
    _session_context: str = Depends(set_session_context),
):
    """
    Share a shopping list with another user by email.
    """
    # Get shopping list with permission check
    shopping_list = await helpers.get_shopping_list_by_id(
        list_id, session, current_user
    )

    # Only owner can share
    if shopping_list.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owner can share the list",
        )

    # Use service to handle sharing logic
    shopping_list = await services.SharingService.share_list_with_user(
        shopping_list, share_data.email, current_user, session
    )

    return await helpers.build_shopping_list_response(
        shopping_list, session, current_user
    )


@router.delete("/{list_id}/share/{user_email}", response_model=ShoppingListRead)
async def remove_member_from_list(
    list_id: int,
    user_email: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(current_user),
    _session_context: str = Depends(set_session_context),
):
    """
    Remove a member from a shared shopping list.
    Only the owner can remove members.
    """
    # Get shopping list with permission check
    shopping_list = await helpers.get_shopping_list_by_id(
        list_id, session, current_user
    )

    # Only owner can remove members
    if shopping_list.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owner can remove members",
        )

    # Use service to handle member removal
    shopping_list = await services.SharingService.remove_member_from_list(
        shopping_list, user_email, current_user, session
    )

    return shopping_list
