from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
import logging

from app.core.fastapi_users import current_user  # Use the same dependency as users.py
from app.models import User
from app.models.shopping_list import ShoppingList
from app.models.item import Item
from app.models.category import Category
from app.schemas.shopping_list import (
    ShoppingListRead,
    ShoppingListCreate,
    ShoppingListUpdate,
)
from app.schemas.item import ItemCreate, ItemRead
from app.schemas.user import UserRead
from app.schemas.share import ShareRequest
from app.api.deps import get_session
from app.services.notification_service import send_list_invitation_email
from app.services.ai_service import ai_service
from app.services.websocket_service import websocket_service

logger = logging.getLogger(__name__)
router = APIRouter()


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

    from app.schemas.user import UserRead
    from app.schemas.item import ItemRead

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
        # Build Pydantic models with items and members
        result_models = []
        for l in lists:
            # Sort items by category before converting to Pydantic models
            sorted_items = sort_items_by_category(l.items) if l.items else []
            items = [
                ItemRead.model_validate(i, from_attributes=True) for i in sorted_items
            ]
            # Members: shared_with + owner if not already included
            members = [
                UserRead.model_validate(u, from_attributes=True) for u in l.shared_with
            ]
            if l.owner_id != current_user.id:
                members.append(UserRead.model_validate(l.owner, from_attributes=True))
            result_models.append(
                ShoppingListRead(
                    id=l.id,
                    name=l.name,
                    description=l.description,
                    owner_id=l.owner_id,
                    created_at=l.created_at,
                    updated_at=l.updated_at,
                    items=items,
                    members=members,
                )
            )
        return result_models
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
    shopping_list = await get_shopping_list_by_id(list_id, session, current_user)

    # Use helper function to build proper Pydantic response
    # The helper will handle eager loading, sorting, and conversion to Pydantic models
    return await build_shopping_list_response(shopping_list, session, current_user)


@router.put("/{list_id}", response_model=ShoppingListRead)
async def update_shopping_list(
    list_id: int,
    list_in: ShoppingListUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(current_user),
):
    """
    Update a shopping list details.
    """
    # Capture user ID early to avoid async context issues
    current_user_id = str(current_user.id)

    # Get shopping list with permission check
    shopping_list = await get_shopping_list_by_id(list_id, session, current_user)

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
        await websocket_service.notify_list_updated(
            list_id=shopping_list.id, list_data=list_data, user_id=current_user_id
        )
    except Exception:
        logger.exception("Failed to send WebSocket list_updated notification")

    return list_read


@router.delete("/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shopping_list(
    list_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(current_user),
):
    """
    Delete a shopping list.
    """
    # Capture user ID before any database operations to avoid async context issues
    user_id = str(current_user.id)

    # Get shopping list with permission check
    shopping_list = await get_shopping_list_by_id(list_id, session, current_user)
    await session.delete(shopping_list)
    await session.commit()

    # Notify via WebSocket
    try:
        await websocket_service.notify_list_deleted(
            list_id=shopping_list.id, user_id=user_id
        )
    except Exception:
        logger.exception("Failed to send WebSocket list_deleted notification")


@router.post("/{list_id}/items", response_model=ItemRead)
async def create_item_for_list(
    list_id: int,
    item_in: ItemCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(current_user),
):
    """
    Add an item to a specific shopping list.
    Uses AI to automatically categorize items and standardize names.
    """
    # Get shopping list with permission check
    shopping_list = await get_shopping_list_by_id(list_id, session, current_user)
    user_id = current_user.id

    # Use AI to suggest category and standardize name
    category = None
    standardized_name = None
    translations = None
    icon_name = None

    try:
        # Get existing categories for AI context
        categories_result = await session.execute(select(Category))
        existing_categories = categories_result.scalars().all()
        category_names = [cat.name for cat in existing_categories]

        # OPTIMIZED: Run AI calls in parallel with timeout
        import asyncio

        # Start category and translation tasks in parallel
        category_task = asyncio.create_task(
            ai_service.suggest_category_async(item_in.name, category_names)
        )
        translation_task = asyncio.create_task(
            ai_service.standardize_and_translate_item_name(item_in.name)
        )

        # Wait for both with timeout (max 10 seconds each)
        try:
            category_name, standardization_result = await asyncio.wait_for(
                asyncio.gather(category_task, translation_task, return_exceptions=True),
                timeout=15.0,  # Max 15 seconds for both calls
            )

            # Handle category result
            if isinstance(category_name, Exception):
                logger.error(f"Category suggestion failed: {category_name}")
                category_name = None
            elif category_name:
                category = await get_or_create_category(category_name, session)

            # Handle translation result
            if isinstance(standardization_result, Exception):
                logger.error(f"Translation failed: {standardization_result}")
                standardization_result = {}

            standardized_name = (
                standardization_result.get("standardized_name")
                if standardization_result
                else None
            )
            translations = (
                standardization_result.get("translations", {})
                if standardization_result
                else {}
            )

            # Get icon suggestion only if we have a category (can't parallelize this one)
            if category:
                try:
                    icon_name = await asyncio.wait_for(
                        ai_service.suggest_icon(item_in.name, category.name),
                        timeout=10.0,  # Max 10 seconds for icon
                    )
                except asyncio.TimeoutError:
                    logger.warning(
                        f"Icon suggestion timed out for item '{item_in.name}'"
                    )
                    icon_name = "shopping_cart"  # Default fallback
                except Exception as e:
                    logger.error(f"Icon suggestion failed: {e}")
                    icon_name = "shopping_cart"  # Default fallback

        except asyncio.TimeoutError:
            logger.warning(
                f"AI processing timed out for item '{item_in.name}' - using fallbacks"
            )
            category_name = None
            standardized_name = None
            translations = {}

    except Exception as e:
        # Log the error but continue with item creation
        logger.error(f"Error during AI processing for item '{item_in.name}': {e}")

        # Fallback: use provided category if any
        if item_in.category_name:
            category = await get_or_create_category(item_in.category_name, session)

    # Create new item with AI-enhanced data
    db_item = Item(
        name=item_in.name,
        quantity=item_in.quantity,
        comment=item_in.comment,
        shopping_list_id=shopping_list.id,
        owner_id=user_id,
        last_modified_by_id=user_id,
        category_id=category.id if category else None,
        icon_name=icon_name
        or (item_in.icon_name if hasattr(item_in, "icon_name") else None),
        standardized_name=standardized_name,
        translations=translations,
        # New structured quantity fields
        quantity_value=item_in.quantity_value,
        quantity_unit_id=item_in.quantity_unit_id,
        quantity_display_text=item_in.quantity_display_text,
    )

    session.add(db_item)
    await session.commit()
    await session.refresh(db_item)
    # Eagerly load relationships for response
    await session.refresh(db_item, attribute_names=["category", "owner"])

    # Send real-time notification to list members
    try:
        from app.schemas.item import ItemRead

        item_data = ItemRead.model_validate(db_item, from_attributes=True).model_dump(
            mode="json"
        )
        await websocket_service.notify_item_created(
            list_id=list_id, item_data=item_data, user_id=str(user_id)
        )
    except Exception as e:
        logger.error(f"Failed to send WebSocket notification for item creation: {e}")
        logger.exception("Full exception details:")

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
    shopping_list = await get_shopping_list_by_id(list_id, session, current_user)
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
):
    """
    Share a shopping list with another user by email.
    """
    # Capture user data early to avoid async context issues
    current_user_id = str(current_user.id)
    current_user_email = current_user.email

    # Get shopping list with permission check
    shopping_list = await get_shopping_list_by_id(list_id, session, current_user)

    # Only owner can share
    if shopping_list.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owner can share the list",
        )

    # Find the user to share with
    result = await session.execute(select(User).where(User.email == share_data.email))
    user_to_share_with = result.scalars().first()

    if not user_to_share_with:
        # User doesn't exist - send invitation email instead of error
        logger.info(
            f"Sending invitation email to non-existent user: {share_data.email}"
        )
        try:
            # Prepare list data for notifications - manually create serializable data
            list_data = {
                "id": shopping_list.id,
                "name": shopping_list.name,
                "description": shopping_list.description,
                "owner_id": str(shopping_list.owner_id),
                "created_at": shopping_list.created_at.isoformat(),
                "updated_at": shopping_list.updated_at.isoformat(),
                "members": [],  # Empty for non-existent user
            }

            await send_list_invitation_email(
                to_email=share_data.email,
                list_data=list_data,
                inviter_email=current_user_email,
            )
            logger.info(f"Invitation email sent successfully to {share_data.email}")
        except Exception:
            logger.exception(f"Failed to send invitation email to {share_data.email}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send invitation email. Please try again.",
            )

        # Return the shopping list without changes (user will be added when they register)
        return await build_shopping_list_response(shopping_list, session, current_user)

    # User exists - proceed with normal sharing
    # Check if already shared
    if user_to_share_with in shopping_list.shared_with:
        return await build_shopping_list_response(
            shopping_list, session, current_user
        )  # Already shared, just return the list

    # Add the user to shared_with
    shopping_list.shared_with.append(user_to_share_with)
    await session.commit()

    # Refresh to get updated relationships
    await session.refresh(shopping_list, attribute_names=["shared_with", "owner"])

    # Update list data with new member - manually create serializable data
    list_data = {
        "id": shopping_list.id,
        "name": shopping_list.name,
        "description": shopping_list.description,
        "owner_id": str(shopping_list.owner_id),
        "created_at": shopping_list.created_at.isoformat(),
        "updated_at": shopping_list.updated_at.isoformat(),
        "members": [
            {"email": u.email, "id": str(u.id)} for u in shopping_list.shared_with
        ],
    }

    # Send notifications: WebSocket and email
    # WebSocket
    try:
        await websocket_service.notify_list_shared(
            list_id=list_id,
            list_data=list_data,
            new_member_email=share_data.email,
            user_id=current_user_id,
        )
    except Exception:
        logger.exception("Failed to send WebSocket list_shared notification")
    # Email notification for existing user
    try:
        await send_list_invitation_email(
            to_email=share_data.email,
            list_data=list_data,
            inviter_email=current_user_email,
        )
    except Exception:
        logger.exception("Failed to send list invitation email")

    return await build_shopping_list_response(shopping_list, session, current_user)


@router.delete("/{list_id}/share/{user_email}", response_model=ShoppingListRead)
async def remove_member_from_list(
    list_id: int,
    user_email: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(current_user),
):
    """
    Remove a member from a shared shopping list.
    Only the owner can remove members.
    """
    # Capture user ID early to avoid async context issues
    current_user_id = str(current_user.id)

    # Get shopping list with permission check
    shopping_list = await get_shopping_list_by_id(list_id, session, current_user)

    # Only owner can remove members
    if shopping_list.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owner can remove members",
        )

    # Find the user to remove
    result = await session.execute(select(User).where(User.email == user_email))
    user_to_remove = result.scalars().first()

    if not user_to_remove:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {user_email} not found",
        )

    # Remove the user from shared_with if they're in the list
    if user_to_remove in shopping_list.shared_with:
        shopping_list.shared_with.remove(user_to_remove)
        await session.commit()

    # Refresh to get updated relationships
    await session.refresh(shopping_list, attribute_names=["shared_with", "owner"])

    # Send real-time notification
    try:
        from app.schemas.shopping_list import ShoppingListRead

        list_data = ShoppingListRead.model_validate(
            shopping_list, from_attributes=True
        ).model_dump(mode="json")
        await websocket_service.notify_member_removed(
            list_id=list_id,
            list_data=list_data,
            removed_member_email=user_email,
            user_id=current_user_id,
        )
    except Exception:
        logger.exception("Failed to send WebSocket member_removed notification")

    return shopping_list


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
