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
from app.schemas.shopping_list import ShoppingListRead, ShoppingListCreate, ShoppingListUpdate
from app.schemas.item import ItemCreate, ItemRead
from app.schemas.user import UserRead
from app.schemas.share import ShareRequest
from app.api.deps import get_session
from app.services.ai_service import ai_service

logger = logging.getLogger(__name__)
router = APIRouter()

async def get_or_create_category(name: str, session: AsyncSession) -> Category:
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
        name=list_in.name,
        description=list_in.description,
        owner_id=current_user.id
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
    members = [UserRead.model_validate(u, from_attributes=True) for u in db_list.shared_with]
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
        members=members
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
                selectinload(ShoppingList.shared_with)
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
                    selectinload(ShoppingList.items).selectinload(Item.last_modified_by),
                    selectinload(ShoppingList.shared_with)
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
            items = [ItemRead.model_validate(i, from_attributes=True) for i in sorted_items]
            # Members: shared_with + owner if not already included
            members = [UserRead.model_validate(u, from_attributes=True) for u in l.shared_with]
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
                    members=members
                )
            )
        return result_models
    except Exception as e:
        print(f"Error in read_shopping_lists: {e}")
        raise


@router.get("/{list_id}", response_model=ShoppingListRead)
async def read_shopping_list(
    *,
    list_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(current_user),
):
    """
    Get a specific shopping list by ID.
    """
    # Check if the list is owned by the user
    result = await session.execute(
        select(ShoppingList)
        .where(
            ShoppingList.id == list_id,
            ShoppingList.owner_id == current_user.id
        )
        .options(
            selectinload(ShoppingList.items).selectinload(Item.category),
            selectinload(ShoppingList.items).selectinload(Item.owner),
            selectinload(ShoppingList.items).selectinload(Item.last_modified_by),
            selectinload(ShoppingList.shared_with)
        )
    )
    shopping_list = result.scalars().first()
    
    # If not owned by user, check if it's shared with the user
    if not shopping_list:
        result = await session.execute(
            select(ShoppingList)
            .where(ShoppingList.id == list_id)
            .join(ShoppingList.shared_with.and_(User.id == current_user.id))
            .options(
                selectinload(ShoppingList.items).selectinload(Item.category),
                selectinload(ShoppingList.items).selectinload(Item.owner),
                selectinload(ShoppingList.items).selectinload(Item.last_modified_by),
                selectinload(ShoppingList.shared_with)
            )
        )
        shopping_list = result.scalars().first()
    
    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list not found or you don't have access"
        )
    
    # Sort items by category before returning
    if shopping_list.items:
        shopping_list.items = sort_items_by_category(shopping_list.items)
    
    # Populate members (users with whom the list is shared plus the owner if the viewer is not the owner)
    shopping_list.members = shopping_list.shared_with + ([shopping_list.owner] if shopping_list.owner_id != current_user.id else [])
    
    return shopping_list


@router.put("/{list_id}", response_model=ShoppingListRead)
async def update_shopping_list(
    *,
    list_id: int,
    list_in: ShoppingListUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(current_user),
):
    """
    Update a shopping list details.
    """
    # First, check if the list exists and belongs to the current user
    result = await session.execute(
        select(ShoppingList).where(
            ShoppingList.id == list_id,
            ShoppingList.owner_id == current_user.id
        )
    )
    shopping_list = result.scalars().first()
    
    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list not found or you don't have access"
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
        .options(selectinload(ShoppingList.items), selectinload(ShoppingList.shared_with), selectinload(ShoppingList.owner))
    )
    shopping_list = result.scalars().first()

    # Build Pydantic response with items and members
    items = [ItemRead.model_validate(i, from_attributes=True) for i in shopping_list.items] if shopping_list.items else []
    members = [UserRead.model_validate(u, from_attributes=True) for u in shopping_list.shared_with]
    if shopping_list.owner_id != current_user.id:
        members.append(UserRead.model_validate(shopping_list.owner, from_attributes=True))
    return ShoppingListRead.model_validate(shopping_list, from_attributes=True, context={"items": items, "members": members})


@router.delete("/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shopping_list(
    *,
    list_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(current_user),
):
    """
    Delete a shopping list.
    """
    # First, check if the list exists and belongs to the current user
    result = await session.execute(
        select(ShoppingList).where(
            ShoppingList.id == list_id,
            ShoppingList.owner_id == current_user.id
        )
    )
    shopping_list = result.scalars().first()
    
    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list not found or you don't have access"
        )
    
    # Delete the shopping list
    await session.delete(shopping_list)
    await session.commit()
    
    return None


@router.post("/{list_id}/items", response_model=ItemRead)
async def create_item_for_list(
    *,
    list_id: int,
    item_in: ItemCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(current_user),
):
    """
    Add an item to a specific shopping list.
    Uses AI to automatically categorize items and standardize names.
    """
    # Extract all needed scalar values from current_user at the very start
    user_id = current_user.id

    # Check if the shopping list exists and belongs to the user
    result = await session.execute(
        select(ShoppingList).where(
            ShoppingList.id == list_id,
            ShoppingList.owner_id == user_id
        )
    )
    shopping_list = result.scalars().first()
    
    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list not found or you don't have access"
        )
    
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
                timeout=15.0  # Max 15 seconds for both calls
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
            
            standardized_name = standardization_result.get("standardized_name") if standardization_result else None
            translations = standardization_result.get("translations", {}) if standardization_result else {}
            
            # Get icon suggestion only if we have a category (can't parallelize this one)
            if category:
                try:
                    icon_name = await asyncio.wait_for(
                        ai_service.suggest_icon(item_in.name, category.name),
                        timeout=10.0  # Max 10 seconds for icon
                    )
                except asyncio.TimeoutError:
                    logger.warning(f"Icon suggestion timed out for item '{item_in.name}'")
                    icon_name = "shopping_cart"  # Default fallback
                except Exception as e:
                    logger.error(f"Icon suggestion failed: {e}")
                    icon_name = "shopping_cart"  # Default fallback
                    
        except asyncio.TimeoutError:
            logger.warning(f"AI processing timed out for item '{item_in.name}' - using fallbacks")
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
        description=item_in.description,
        shopping_list_id=list_id,
        owner_id=user_id,
        last_modified_by_id=user_id,
        category_id=category.id if category else None,
        icon_name=icon_name or (item_in.icon_name if hasattr(item_in, 'icon_name') else None),
        standardized_name=standardized_name,
        translations=translations
    )
    
    session.add(db_item)
    await session.commit()
    await session.refresh(db_item)
    # Eagerly load relationships for response
    await session.refresh(db_item, attribute_names=["category", "owner"])
    return db_item


@router.get("/{list_id}/items", response_model=List[ItemRead])
async def read_items_from_list(
    *,
    list_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(current_user),
):
    """
    Get all items from a specific shopping list.
    """
    # Check if the shopping list exists and belongs to the user
    result = await session.execute(
        select(ShoppingList).where(
            ShoppingList.id == list_id,
            ShoppingList.owner_id == current_user.id
        )
    )
    shopping_list = result.scalars().first()
    
    if not shopping_list:
        # Check if it's shared with the user
        result = await session.execute(
            select(ShoppingList).where(
                ShoppingList.id == list_id
            ).join(
                ShoppingList.shared_with.and_(User.id == current_user.id)
            )
        )
        shopping_list = result.scalars().first()
        
        if not shopping_list:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shopping list not found or you don't have access"
            )
    # Eagerly load category for all items
    result = await session.execute(
        select(Item).where(Item.shopping_list_id == list_id).options(selectinload(Item.category), selectinload(Item.shopping_list), selectinload(Item.owner))
    )
    items = result.scalars().all()
    return items


@router.post("/{list_id}/share", response_model=ShoppingListRead)
async def share_shopping_list(
    *,
    list_id: int,
    share_data: ShareRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(current_user),
):
    """
    Share a shopping list with another user by email.
    """
    # First, check if the list exists and belongs to the current user
    result = await session.execute(
        select(ShoppingList).where(
            ShoppingList.id == list_id,
            ShoppingList.owner_id == current_user.id
        )
    )
    shopping_list = result.scalars().first()
    
    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list not found or you don't have access"
        )
    
    # Find the user to share with
    result = await session.execute(
        select(User).where(User.email == share_data.email)
    )
    user_to_share_with = result.scalars().first()
    
    if not user_to_share_with:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {share_data.email} not found"
        )
    
    # Check if already shared
    if user_to_share_with in shopping_list.shared_with:
        return shopping_list  # Already shared, just return the list
    
    # Add the user to shared_with
    shopping_list.shared_with.append(user_to_share_with)
    await session.commit()
    
    # Populate members
    shopping_list.members = shopping_list.shared_with + [shopping_list.owner]
    
    return shopping_list

from app.core.fastapi_users import current_user
from app.models import User, ShoppingList, Item
from app.schemas.shopping_list import ShoppingListRead, ShoppingListCreate, ShoppingListUpdate
from app.schemas.user import UserRead
from app.schemas.item import ItemRead
from app.api.deps import get_session

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

