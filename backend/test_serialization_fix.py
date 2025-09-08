#!/usr/bin/env python3
"""
Test script to verify that the share endpoint works correctly with serialization fix.
"""
import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, "/home/honzik/GitHub/FamilyCart/FamilyCart/backend")

from app.core.config import settings
from app.db.session import get_session
from app.models.user import User
from app.models.shopping_list import ShoppingList
from app.models.item import Item
from app.schemas.shopping_list import ShoppingListRead
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


async def test_serialization():
    """Test that shopping list with items can be properly serialized"""
    print("Testing shopping list serialization...")

    # Get a database session
    async for session in get_session():
        try:
            # Find a test user
            result = await session.execute(
                select(User).where(User.email == "test1@example.com")
            )
            user = result.scalars().first()

            if not user:
                print("❌ Test user 'test1@example.com' not found")
                return False

            print(f"✅ Found test user: {user.email}")

            # Find their shopping list with items
            result = await session.execute(
                select(ShoppingList)
                .options(
                    selectinload(ShoppingList.items),
                    selectinload(ShoppingList.shared_with),
                    selectinload(ShoppingList.owner),
                )
                .where(ShoppingList.owner_id == user.id)
            )
            shopping_list = result.scalars().first()

            if not shopping_list:
                print("❌ No shopping list found for test user")
                return False

            print(f"✅ Found shopping list: {shopping_list.name}")
            print(f"   Items count: {len(shopping_list.items)}")

            # Try to serialize the shopping list using ShoppingListRead schema
            try:
                list_data = ShoppingListRead.model_validate(
                    shopping_list, from_attributes=True
                )
                print("✅ Successfully validated shopping list with Pydantic schema")

                # Try to convert to JSON-serializable dict
                json_data = list_data.model_dump(mode="json")
                print("✅ Successfully converted to JSON-serializable dict")
                print(f"   Serialized items count: {len(json_data.get('items', []))}")

                return True

            except Exception as e:
                print(f"❌ Failed to serialize shopping list: {e}")
                print(f"   Error type: {type(e).__name__}")
                return False

        except Exception as e:
            print(f"❌ Database error: {e}")
            return False


if __name__ == "__main__":
    result = asyncio.run(test_serialization())
    if result:
        print("\n🎉 Serialization test PASSED!")
        sys.exit(0)
    else:
        print("\n💥 Serialization test FAILED!")
        sys.exit(1)
