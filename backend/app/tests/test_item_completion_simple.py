"""
Simple test for item completion functionality - without complex fixture dependencies.
"""
import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ShoppingList, Item, Category


@pytest.mark.asyncio
async def test_update_item_completion_status_simple(client: AsyncClient, test_db: AsyncSession, test_user: dict, token_header: dict):
    """Test updating item completion status without complex fixtures."""
    
    # Create category directly
    category = Category(name=f"TestCategory-{uuid.uuid4().hex[:8]}")
    test_db.add(category)
    await test_db.commit()
    await test_db.refresh(category)
    category_id = category.id  # Store ID immediately
    
    # Create shopping list directly
    shopping_list = ShoppingList(
        name="Test Shopping List",
        description="Test list for item completion",
        owner_id=test_user["id"]
    )
    test_db.add(shopping_list)
    await test_db.commit()
    await test_db.refresh(shopping_list)
    shopping_list_id = shopping_list.id  # Store ID immediately
    
    # Create item directly
    item = Item(
        name="Test Item",
        quantity="1",
        comment="Test item for completion",
        shopping_list_id=shopping_list_id,
        owner_id=test_user["id"],
        last_modified_by_id=test_user["id"],
        category_id=category_id,
        is_completed=False
    )
    test_db.add(item)
    await test_db.commit()
    await test_db.refresh(item)
    item_id = item.id  # Store ID immediately
    
    # Test the completion toggle
    response = await client.put(
        f"/api/v1/items/{item_id}",
        json={"is_completed": True},
        headers=token_header
    )
    
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["is_completed"] is True
    assert response_data["last_modified_by"]["id"] == str(test_user["id"])
    

@pytest.mark.asyncio
async def test_update_item_completion_back_to_false_simple(client: AsyncClient, test_db: AsyncSession, test_user: dict, token_header: dict):
    """Test toggling item completion back to false."""
    
    # Create category directly
    category = Category(name=f"TestCategory-{uuid.uuid4().hex[:8]}")
    test_db.add(category)
    await test_db.commit()
    await test_db.refresh(category)
    category_id = category.id  # Store ID immediately
    
    # Create shopping list directly
    shopping_list = ShoppingList(
        name="Test Shopping List",
        description="Test list for item completion",
        owner_id=test_user["id"]
    )
    test_db.add(shopping_list)
    await test_db.commit()
    await test_db.refresh(shopping_list)
    shopping_list_id = shopping_list.id  # Store ID immediately
    
    # Create item directly - already completed
    item = Item(
        name="Test Item",
        quantity="1",
        comment="Test item for completion",
        shopping_list_id=shopping_list_id,
        owner_id=test_user["id"],
        last_modified_by_id=test_user["id"],
        category_id=category_id,
        is_completed=True  # Start as completed
    )
    test_db.add(item)
    await test_db.commit()
    await test_db.refresh(item)
    item_id = item.id  # Store ID immediately
    
    # Test toggling back to incomplete
    response = await client.put(
        f"/api/v1/items/{item_id}",
        json={"is_completed": False},
        headers=token_header
    )
    
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["is_completed"] is False
    assert response_data["last_modified_by"]["id"] == str(test_user["id"])
