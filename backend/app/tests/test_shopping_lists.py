"""
Tests for shopping list endpoints.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, ShoppingList, Item, Category
from app.core.fastapi_users import current_user

# Shared fixture for creating test data
@pytest.fixture
async def test_shopping_list(test_db: AsyncSession, test_user: dict):
    """Create a test shopping list with items."""
    # Create a shopping list
    shopping_list = ShoppingList(
        name="Test Shopping List",
        description="This is a test shopping list",
        owner_id=test_user["id"]
    )
    test_db.add(shopping_list)
    await test_db.commit()
    await test_db.refresh(shopping_list)

    # Create a category
    category = Category(name="Test Category")
    test_db.add(category)
    await test_db.commit()
    await test_db.refresh(category)

    # Add items to the list
    item1 = Item(
        name="Item 1",
        quantity="1",
        comment="First test item",
        shopping_list_id=shopping_list.id,
        owner_id=test_user["id"],
        category_id=category.id
    )
    
    item2 = Item(
        name="Item 2",
        quantity="2",
        comment="Second test item",
        shopping_list_id=shopping_list.id,
        owner_id=test_user["id"],
        category_id=category.id
    )
    
    test_db.add_all([item1, item2])
    await test_db.commit()
    
    return shopping_list

@pytest.mark.asyncio
async def test_create_shopping_list(client: AsyncClient, token_header):
    """Test creating a shopping list."""
    response = await client.post(
        "/api/v1/shopping-lists/",
        headers=token_header,
        json={"name": "New List", "description": "Brand new list"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New List"
    assert data["description"] == "Brand new list"
    assert "id" in data
    assert "owner_id" in data
    assert "created_at" in data
    assert "updated_at" in data

@pytest.mark.asyncio
async def test_get_shopping_lists(client: AsyncClient, token_header, test_shopping_list):
    """Test getting all shopping lists for a user."""
    response = await client.get(
        "/api/v1/shopping-lists/",
        headers=token_header
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(sl["name"] == "Test Shopping List" for sl in data)
    
    # Verify structure of returned data
    shopping_list = next(sl for sl in data if sl["name"] == "Test Shopping List")
    assert "id" in shopping_list
    assert "owner_id" in shopping_list
    assert "items" in shopping_list
    assert "members" in shopping_list

@pytest.mark.asyncio
async def test_get_shopping_list(client: AsyncClient, token_header, test_shopping_list):
    """Test getting a specific shopping list."""
    response = await client.get(
        f"/api/v1/shopping-lists/{test_shopping_list.id}",
        headers=token_header
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Shopping List"
    assert data["description"] == "This is a test shopping list"
    assert "items" in data
    assert "members" in data

@pytest.mark.asyncio
async def test_update_shopping_list(client: AsyncClient, token_header, test_shopping_list):
    """Test updating a shopping list."""
    response = await client.put(
        f"/api/v1/shopping-lists/{test_shopping_list.id}",
        headers=token_header,
        json={"name": "Updated List Name"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated List Name"
    assert data["description"] == "This is a test shopping list"  # Unchanged

@pytest.mark.asyncio
async def test_delete_shopping_list(client: AsyncClient, token_header, test_shopping_list):
    """Test deleting a shopping list."""
    response = await client.delete(
        f"/api/v1/shopping-lists/{test_shopping_list.id}",
        headers=token_header
    )
    
    assert response.status_code == 204
    
    # Verify it's deleted
    response = await client.get(
        f"/api/v1/shopping-lists/{test_shopping_list.id}",
        headers=token_header
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_add_item_to_shopping_list(client: AsyncClient, token_header, test_shopping_list):
    """Test adding an item to a shopping list."""
    response = await client.post(
        f"/api/v1/shopping-lists/{test_shopping_list.id}/items",
        headers=token_header,
        json={
            "name": "New Test Item",
            "quantity": "3",
            "comment": "A new item for testing",
            "category_name": "Test Category"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Test Item"
    assert data["quantity"] == "3"
    assert data["comment"] == "A new item for testing"
    assert "category" in data
    assert data["category"]["name"] == "Test Category"

@pytest.mark.asyncio
async def test_get_items_from_shopping_list(client: AsyncClient, token_header, test_shopping_list):
    """Test getting items from a shopping list."""
    response = await client.get(
        f"/api/v1/shopping-lists/{test_shopping_list.id}/items",
        headers=token_header
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    assert any(item["name"] == "Item 1" for item in data)
    assert any(item["name"] == "Item 2" for item in data)
