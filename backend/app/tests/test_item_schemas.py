"""
Simple verification test for item completion functionality.
This test verifies the Pydantic schemas and basic logic without requiring database setup.
"""

from datetime import datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.models.item import Item
from app.schemas.item import ItemCreate, ItemRead, ItemUpdate


def test_item_update_schema_includes_is_completed():
    """Test that ItemUpdate schema correctly includes is_completed field."""
    # Test creating ItemUpdate with is_completed
    item_update = ItemUpdate(is_completed=True)
    assert item_update.is_completed is True

    item_update = ItemUpdate(is_completed=False)
    assert item_update.is_completed is False

    # Test that exclude_unset works correctly
    item_update = ItemUpdate(name="Test Item")
    update_dict = item_update.dict(exclude_unset=True)
    assert "name" in update_dict
    assert "is_completed" not in update_dict

    # Test with both name and is_completed
    item_update = ItemUpdate(name="Test Item", is_completed=True)
    update_dict = item_update.dict(exclude_unset=True)
    assert "name" in update_dict
    assert "is_completed" in update_dict
    assert update_dict["is_completed"] is True


def test_item_read_schema_includes_is_completed():
    """Test that ItemRead schema includes is_completed field."""
    # Test serialization with is_completed
    item_data = {
        "id": 1,
        "name": "Test Item",
        "quantity": "1",
        "comment": "Test comment",
        "shopping_list_id": 1,
        "owner_id": str(uuid4()),
        "last_modified_by_id": str(uuid4()),
        "is_completed": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "category": None,
        "icon_name": None,
        "owner": None,
        "last_modified_by": None,
    }

    item_read = ItemRead(**item_data)
    assert item_read.is_completed is True

    # Test serialization to dict
    item_dict = item_read.dict()
    assert "is_completed" in item_dict
    assert item_dict["is_completed"] is True


def test_item_update_validation():
    """Test ItemUpdate validation for is_completed field."""
    # Valid boolean values
    assert ItemUpdate(is_completed=True).is_completed is True
    assert ItemUpdate(is_completed=False).is_completed is False

    # Test with None (should be allowed)
    item_update = ItemUpdate(is_completed=None)
    assert item_update.is_completed is None

    # Test invalid types should raise validation error (Pydantic v2 raises ValidationError)
    with pytest.raises(ValidationError):
        ItemUpdate(is_completed="not_a_boolean")

    # Note: Pydantic v2 allows integer coercion to bool (1 → True, 0 → False)
    # So we don't test for strict integer rejection


def test_item_create_does_not_include_is_completed():
    """Test that ItemCreate doesn't include is_completed (should default to False in model)."""
    item_create = ItemCreate(name="Test Item")
    create_dict = item_create.dict()
    assert "is_completed" not in create_dict
    # This is correct - is_completed should be set to False by default in the model


def test_multiple_field_update_with_completion():
    """Test updating multiple fields including completion status."""
    item_update = ItemUpdate(
        name="Updated Name", quantity="2", comment="Updated comment", is_completed=True
    )

    update_dict = item_update.dict(exclude_unset=True)
    expected_fields = {"name", "quantity", "comment", "is_completed"}
    assert set(update_dict.keys()) == expected_fields
    assert update_dict["is_completed"] is True
    assert update_dict["name"] == "Updated Name"
    assert update_dict["quantity"] == "2"
    assert update_dict["comment"] == "Updated comment"


if __name__ == "__main__":
    # Run basic tests manually
    test_item_update_schema_includes_is_completed()
    test_item_read_schema_includes_is_completed()
    test_item_update_validation()
    test_item_create_does_not_include_is_completed()
    test_multiple_field_update_with_completion()
    print("✅ All item completion schema tests passed!")
