import logging
import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch

from app.models import ShoppingList, Item, Category


@pytest.mark.asyncio
async def test_audit_logging_for_item_completion(client: AsyncClient, test_db: AsyncSession, test_user: dict, token_header: dict):
    """Test that audit logs are generated when item completion status changes."""
    
    # Create category directly
    category = Category(name=f"TestCategory-{uuid.uuid4().hex[:8]}")
    test_db.add(category)
    await test_db.commit()
    await test_db.refresh(category)
    category_id = category.id
    
    # Create shopping list directly
    shopping_list = ShoppingList(
        name="Test List for Audit",
        description="Test list for audit logging",
        owner_id=test_user["id"]
    )
    test_db.add(shopping_list)
    await test_db.commit()
    await test_db.refresh(shopping_list)
    shopping_list_id = shopping_list.id
    
    # Create item directly
    item = Item(
        name="Test Item for Audit",
        quantity="1",
        description="Test item for audit logging",
        shopping_list_id=shopping_list_id,
        owner_id=test_user["id"],
        last_modified_by_id=test_user["id"],
        category_id=category_id,
        is_completed=False
    )
    test_db.add(item)
    await test_db.commit()
    await test_db.refresh(item)
    item_id = item.id
    
    # Test audit logging for marking item as completed
    with patch('app.api.v1.endpoints.items.logger') as mock_logger:
        update_data = {"is_completed": True}
        response = await client.put(f"/api/v1/items/{item_id}", json=update_data, headers=token_header)
        assert response.status_code == 200
        
        # Verify audit log was called
        mock_logger.info.assert_called_once()
        log_call = mock_logger.info.call_args[0][0]
        
        # Check log message contains expected information
        assert "Item status changed" in log_call
        assert test_user["email"] in log_call
        assert str(item_id) in log_call
        assert "Test Item for Audit" in log_call
        assert "completed" in log_call
        assert "Test List for Audit" in log_call
    
    # Test audit logging for marking item as uncompleted
    with patch('app.api.v1.endpoints.items.logger') as mock_logger:
        update_data = {"is_completed": False}
        response = await client.put(f"/api/v1/items/{item_id}", json=update_data, headers=token_header)
        assert response.status_code == 200
        
        # Verify audit log was called
        mock_logger.info.assert_called_once()
        log_call = mock_logger.info.call_args[0][0]
        
        # Check log message contains expected information
        assert "Item status changed" in log_call
        assert test_user["email"] in log_call
        assert str(item_id) in log_call
        assert "Test Item for Audit" in log_call
        assert "uncompleted" in log_call
        assert "Test List for Audit" in log_call


@pytest.mark.asyncio
async def test_no_audit_log_when_completion_status_unchanged(client: AsyncClient, test_db: AsyncSession, test_user: dict, token_header: dict):
    """Test that no audit log is generated when completion status doesn't change."""
    
    # Create category directly
    category = Category(name=f"TestCategory-{uuid.uuid4().hex[:8]}")
    test_db.add(category)
    await test_db.commit()
    await test_db.refresh(category)
    category_id = category.id
    
    # Create shopping list directly
    shopping_list = ShoppingList(
        name="Test List No Audit",
        description="Test list for no audit logging",
        owner_id=test_user["id"]
    )
    test_db.add(shopping_list)
    await test_db.commit()
    await test_db.refresh(shopping_list)
    shopping_list_id = shopping_list.id
    
    # Create item directly
    item = Item(
        name="Test Item No Audit",
        quantity="1",
        description="Test item for no audit logging",
        shopping_list_id=shopping_list_id,
        owner_id=test_user["id"],
        last_modified_by_id=test_user["id"],
        category_id=category_id,
        is_completed=False
    )
    test_db.add(item)
    await test_db.commit()
    await test_db.refresh(item)
    item_id = item.id
    
    # Test updating item name without changing completion status
    with patch('app.api.v1.endpoints.items.logger') as mock_logger:
        update_data = {"name": "Updated Item Name"}
        response = await client.put(f"/api/v1/items/{item_id}", json=update_data, headers=token_header)
        assert response.status_code == 200
        
        # Verify no audit log was called
        mock_logger.info.assert_not_called()


@pytest.mark.asyncio 
async def test_no_audit_log_when_setting_same_completion_status(client: AsyncClient, test_db: AsyncSession, test_user: dict, token_header: dict):
    """Test that no audit log is generated when setting completion status to the same value."""
    
    # Create category directly
    category = Category(name=f"TestCategory-{uuid.uuid4().hex[:8]}")
    test_db.add(category)
    await test_db.commit()
    await test_db.refresh(category)
    category_id = category.id
    
    # Create shopping list directly
    shopping_list = ShoppingList(
        name="Test List Same Status",
        description="Test list for same status",
        owner_id=test_user["id"]
    )
    test_db.add(shopping_list)
    await test_db.commit()
    await test_db.refresh(shopping_list)
    shopping_list_id = shopping_list.id
    
    # Create item directly (default is_completed = False)
    item = Item(
        name="Test Item Same Status",
        quantity="1",
        description="Test item for same status",
        shopping_list_id=shopping_list_id,
        owner_id=test_user["id"],
        last_modified_by_id=test_user["id"],
        category_id=category_id,
        is_completed=False
    )
    test_db.add(item)
    await test_db.commit()
    await test_db.refresh(item)
    item_id = item.id
    
    # Test setting completion status to False (same as default)
    with patch('app.api.v1.endpoints.items.logger') as mock_logger:
        update_data = {"is_completed": False}
        response = await client.put(f"/api/v1/items/{item_id}", json=update_data, headers=token_header)
        assert response.status_code == 200
        
        # Verify no audit log was called since status didn't change
        mock_logger.info.assert_not_called()
