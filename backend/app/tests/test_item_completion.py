"""
Tests for item completion functionality.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import User, ShoppingList, Item, Category


@pytest.fixture
async def test_shopping_list(test_db: AsyncSession, test_user: dict):
    """Create a test shopping list."""
    shopping_list = ShoppingList(
        name="Test List",
        description="Test shopping list for item completion",
        owner_id=test_user["id"]
    )
    test_db.add(shopping_list)
    await test_db.commit()
    await test_db.refresh(shopping_list)
    return shopping_list


@pytest.fixture
async def test_category(test_db: AsyncSession):
    """Create a test category."""
    import uuid
    unique_name = f"Groceries-{uuid.uuid4().hex[:8]}"
    category = Category(name=unique_name)
    test_db.add(category)
    await test_db.commit()
    await test_db.refresh(category)
    return category


@pytest.fixture
async def test_item(test_db: AsyncSession, test_user: dict, test_shopping_list: ShoppingList, test_category: Category):
    """Create a test item."""
    # Ensure the shopping list is fully loaded
    await test_db.refresh(test_shopping_list)
    await test_db.refresh(test_category)
    
    item = Item(
        name="Test Item",
        quantity="1",
        comment="Test item for completion",
        shopping_list_id=test_shopping_list.id,
        owner_id=test_user["id"],
        last_modified_by_id=test_user["id"],
        category_id=test_category.id,
        is_completed=False
    )
    test_db.add(item)
    await test_db.commit()
    await test_db.refresh(item)
    return item


@pytest.mark.asyncio
async def test_update_item_completion_status(client: AsyncClient, token_header: dict, test_item: Item, test_db: AsyncSession):
    """Test updating item completion status via PUT endpoint."""
    # Test marking item as completed
    response = await client.put(
        f"/api/v1/items/{test_item.id}",
        json={"is_completed": True},
        headers=token_header
    )
    
    # Check response
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["is_completed"] is True
    assert response_data["id"] == test_item.id
    assert response_data["name"] == test_item.name
    
    # Verify in database
    result = await test_db.execute(select(Item).where(Item.id == test_item.id))
    updated_item = result.scalars().first()
    assert updated_item.is_completed is True


@pytest.mark.asyncio
async def test_update_item_completion_back_to_false(client: AsyncClient, token_header: dict, test_item: Item, test_db: AsyncSession):
    """Test unchecking a completed item."""
    # First mark item as completed
    test_item.is_completed = True
    test_db.add(test_item)
    await test_db.commit()
    
    # Test marking item as not completed
    response = await client.put(
        f"/api/v1/items/{test_item.id}",
        json={"is_completed": False},
        headers=token_header
    )
    
    # Check response
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["is_completed"] is False
    assert response_data["id"] == test_item.id
    
    # Verify in database
    result = await test_db.execute(select(Item).where(Item.id == test_item.id))
    updated_item = result.scalars().first()
    assert updated_item.is_completed is False


@pytest.mark.asyncio
async def test_update_item_with_multiple_fields_including_completion(client: AsyncClient, token_header: dict, test_user: dict, test_item: Item):
    """Test updating multiple fields including completion status."""
    response = await client.put(
        f"/api/v1/items/{test_item.id}",
        json={
            "name": "Updated Item Name",
            "quantity": "2",
            "is_completed": True
        },
        headers=token_header
    )
    
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["name"] == "Updated Item Name"
    assert response_data["quantity"] == "2"
    assert response_data["is_completed"] is True
    assert response_data["last_modified_by"]["id"] == str(test_user["id"])


@pytest.mark.asyncio
async def test_update_nonexistent_item_completion(client: AsyncClient, token_header: dict):
    """Test updating completion status of non-existent item."""
    response = await client.put(
        "/api/v1/items/99999",
        json={"is_completed": True},
        headers=token_header
    )
    
    assert response.status_code == 404
    assert "Item not found" in response.json()["detail"]


@pytest.mark.asyncio 
async def test_unauthorized_update_item_completion(client: AsyncClient, test_item: Item):
    """Test updating item completion without authorization."""
    response = await client.put(
        f"/api/v1/items/{test_item.id}",
        json={"is_completed": True}
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_item_completion_wrong_owner(client: AsyncClient, test_item: Item, test_db: AsyncSession):
    """Test updating item completion by user who doesn't own the list."""
    # Create another user
    other_user = User(
        email="other@example.com", 
        hashed_password="hashed_password",
        is_active=True,
        is_superuser=False,
        is_verified=True,
        nickname="Other User"
    )
    test_db.add(other_user)
    await test_db.commit()
    await test_db.refresh(other_user)
    
    # Create token for other user
    other_token_response = await client.post(
        "/api/v1/auth/jwt/login",
        data={"username": other_user.email, "password": "password"}
    )
    other_token_data = other_token_response.json()
    other_headers = {"Authorization": f"Bearer {other_token_data['access_token']}"}
    
    response = await client.put(
        f"/api/v1/items/{test_item.id}",
        json={"is_completed": True},
        headers=other_headers
    )
    
    assert response.status_code == 403
    assert "Not authorized to update this item" in response.json()["detail"]


# Edge case tests
@pytest.mark.asyncio
async def test_update_item_completion_with_invalid_data_type(client: AsyncClient, token_header: dict, test_item: Item):
    """Test updating completion with invalid data type."""
    response = await client.put(
        f"/api/v1/items/{test_item.id}",
        json={"is_completed": "not_a_boolean"},
        headers=token_header
    )
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_update_item_completion_preserves_other_fields(client: AsyncClient, token_header: dict, test_item: Item):
    """Test that updating completion status preserves other fields."""
    # Get original item data
    original_name = test_item.name
    original_quantity = test_item.quantity
    original_comment = test_item.comment
    
    response = await client.put(
        f"/api/v1/items/{test_item.id}",
        json={"is_completed": True},
        headers=token_header
    )
    
    assert response.status_code == 200
    response_data = response.json()
    
    # Check that other fields are preserved
    assert response_data["name"] == original_name
    assert response_data["quantity"] == original_quantity
    assert response_data["comment"] == original_comment
    assert response_data["is_completed"] is True
