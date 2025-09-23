"""
Tests for category-based sorting functionality.
"""

import pytest

from app.api.v1.endpoints.shopping_lists import sort_items_by_category
from app.models.category import Category
from app.models.item import Item


class MockCategory:
    """Mock category for testing."""

    def __init__(self, name):
        self.name = name


class MockItem:
    """Mock item for testing."""

    def __init__(self, name, category_name=None, is_completed=False):
        self.name = name
        self.category = MockCategory(category_name) if category_name else None
        self.is_completed = is_completed


def test_sort_items_by_category_basic():
    """Test basic category sorting."""
    items = [
        MockItem("Bread", "Bakery", False),
        MockItem("Milk", "Dairy", False),
        MockItem("Apples", "Produce", False),
        MockItem("Cheese", "Dairy", False),
        MockItem("Random Item", None, False),  # No category
    ]

    sorted_items = sort_items_by_category(items)

    # Should be sorted alphabetically by category, then by item name
    expected_order = [
        "Bread",  # Bakery
        "Cheese",  # Dairy
        "Milk",  # Dairy
        "Apples",  # Produce
        "Random Item",  # No category (comes last)
    ]

    actual_order = [item.name for item in sorted_items]
    assert actual_order == expected_order


def test_sort_items_by_category_with_completion():
    """Test sorting with completion status."""
    items = [
        MockItem("Bread", "Bakery", True),  # Completed
        MockItem("Milk", "Dairy", False),  # Pending
        MockItem("Apples", "Produce", True),  # Completed
        MockItem("Cheese", "Dairy", False),  # Pending
        MockItem("Yogurt", "Dairy", True),  # Completed
        MockItem("Bananas", "Produce", False),  # Pending
    ]

    sorted_items = sort_items_by_category(items)

    # Within each category, pending items should come before completed items
    expected_order = [
        "Bread",  # Bakery - Completed (only item in category)
        "Cheese",  # Dairy - Pending
        "Milk",  # Dairy - Pending
        "Yogurt",  # Dairy - Completed
        "Bananas",  # Produce - Pending
        "Apples",  # Produce - Completed
    ]

    actual_order = [item.name for item in sorted_items]
    assert actual_order == expected_order


def test_sort_items_by_category_mixed_scenarios():
    """Test sorting with mixed scenarios including no categories."""
    items = [
        MockItem("Zucchini", "Produce", False),
        MockItem("Item Z", None, False),  # No category
        MockItem("Ale", "Beverages", True),  # Completed
        MockItem("Butter", "Dairy", False),
        MockItem("Item A", None, True),  # No category, completed
        MockItem("Beer", "Beverages", False),  # Pending
        MockItem("Apple", "Produce", True),  # Completed
    ]

    sorted_items = sort_items_by_category(items)

    # Expected: Beverages (Beer pending, Ale completed), Dairy (Butter), Produce (Zucchini pending, Apple completed), then no-category items
    expected_order = [
        "Beer",  # Beverages - Pending
        "Ale",  # Beverages - Completed
        "Butter",  # Dairy - Pending
        "Zucchini",  # Produce - Pending
        "Apple",  # Produce - Completed
        "Item Z",  # No category - Pending
        "Item A",  # No category - Completed
    ]

    actual_order = [item.name for item in sorted_items]
    assert actual_order == expected_order


def test_sort_items_by_category_empty_list():
    """Test sorting with empty list."""
    items = []
    sorted_items = sort_items_by_category(items)
    assert sorted_items == []


def test_sort_items_by_category_single_item():
    """Test sorting with single item."""
    items = [MockItem("Single Item", "Test Category", False)]
    sorted_items = sort_items_by_category(items)
    assert len(sorted_items) == 1
    assert sorted_items[0].name == "Single Item"


def test_sort_items_by_category_case_insensitive():
    """Test that sorting is case insensitive for item names."""
    items = [
        MockItem("zebra", "Animals", False),
        MockItem("Apple", "Animals", False),
        MockItem("bear", "Animals", False),
    ]

    sorted_items = sort_items_by_category(items)

    # Should be sorted case-insensitively: Apple, bear, zebra
    expected_order = ["Apple", "bear", "zebra"]
    actual_order = [item.name for item in sorted_items]
    assert actual_order == expected_order


if __name__ == "__main__":
    # Run basic tests
    test_sort_items_by_category_basic()
    test_sort_items_by_category_with_completion()
    test_sort_items_by_category_mixed_scenarios()
    test_sort_items_by_category_empty_list()
    test_sort_items_by_category_single_item()
    test_sort_items_by_category_case_insensitive()
    print("All category sorting tests passed!")
