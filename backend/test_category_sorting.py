"""
Test category-based sorting functionality
"""

import pytest

from app.api.v1.endpoints.shopping_lists import sort_items_by_category
from app.models import Category, Item, ShoppingList, User
from app.tests.conftest import (
    create_test_category,
    create_test_shopping_list,
    create_test_user,
)


def test_sort_items_by_category_basic():
    """Test basic category sorting functionality"""
    # Create mock items with different categories
    dairy_category = Category(id=1, name="Dairy")
    produce_category = Category(id=2, name="Produce")
    meat_category = Category(id=3, name="Meat")

    # Create items with different completion status and categories
    items = [
        Item(id=1, name="Chicken", category=meat_category, is_completed=False),
        Item(id=2, name="Milk", category=dairy_category, is_completed=True),
        Item(id=3, name="Apples", category=produce_category, is_completed=False),
        Item(id=4, name="Cheese", category=dairy_category, is_completed=False),
        Item(id=5, name="Bread", category=None, is_completed=False),  # No category
        Item(id=6, name="Bananas", category=produce_category, is_completed=True),
    ]

    sorted_items = sort_items_by_category(items)

    # Check that items are sorted by:
    # 1. Category name (alphabetically)
    # 2. Completion status (uncompleted first)
    # 3. Item name (alphabetically)

    expected_order = [
        "Cheese",  # Dairy, uncompleted
        "Milk",  # Dairy, completed
        "Chicken",  # Meat, uncompleted
        "Apples",  # Produce, uncompleted
        "Bananas",  # Produce, completed
        "Bread",  # No category (comes last)
    ]

    actual_order = [item.name for item in sorted_items]
    assert actual_order == expected_order


def test_sort_items_by_category_same_category():
    """Test sorting within the same category"""
    dairy_category = Category(id=1, name="Dairy")

    items = [
        Item(id=1, name="Yogurt", category=dairy_category, is_completed=True),
        Item(id=2, name="Milk", category=dairy_category, is_completed=False),
        Item(id=3, name="Butter", category=dairy_category, is_completed=False),
        Item(id=4, name="Cheese", category=dairy_category, is_completed=True),
    ]

    sorted_items = sort_items_by_category(items)

    # Within the same category, uncompleted items should come first,
    # then sorted alphabetically by name
    expected_order = ["Butter", "Milk", "Cheese", "Yogurt"]
    actual_order = [item.name for item in sorted_items]
    assert actual_order == expected_order


def test_sort_items_by_category_no_category():
    """Test sorting items without categories"""
    items = [
        Item(id=1, name="Zebra item", category=None, is_completed=False),
        Item(id=2, name="Apple item", category=None, is_completed=True),
        Item(id=3, name="Banana item", category=None, is_completed=False),
    ]

    sorted_items = sort_items_by_category(items)

    # Items without categories should be sorted by completion status, then name
    expected_order = ["Banana item", "Zebra item", "Apple item"]
    actual_order = [item.name for item in sorted_items]
    assert actual_order == expected_order


def test_sort_items_by_category_empty_list():
    """Test sorting empty list"""
    sorted_items = sort_items_by_category([])
    assert sorted_items == []


def test_sort_items_by_category_mixed_case():
    """Test sorting with mixed case category and item names"""
    category_a = Category(id=1, name="Category A")
    category_b = Category(id=2, name="category b")  # lowercase

    items = [
        Item(id=1, name="zebra", category=category_b, is_completed=False),
        Item(id=2, name="Apple", category=category_a, is_completed=False),
        Item(id=3, name="banana", category=category_b, is_completed=False),
    ]

    sorted_items = sort_items_by_category(items)

    # Categories should be sorted alphabetically (case-sensitive)
    # Items within categories should be sorted by lowercase name
    expected_order = ["Apple", "banana", "zebra"]
    actual_order = [item.name for item in sorted_items]
    assert actual_order == expected_order
