#!/usr/bin/env python3
"""
Direct test of the sharing serialization issue by calling the share function directly.
"""
import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, "/home/honzik/GitHub/FamilyCart/FamilyCart/backend")

from app.db.session import get_session
from app.models.user import User
from app.models.shopping_list import ShoppingList
from app.schemas.shopping_list import ShoppingListRead, ShareRequest
from app.api.v1.endpoints.shopping_lists import share_shopping_list
from sqlalchemy import select
from sqlalchemy.orm import selectinload


async def test_share_serialization():
    """Test shopping list sharing and serialization directly"""
    print("Testing shopping list sharing serialization...")

    async for session in get_session():
        try:
            # Get the test user (owner)
            result = await session.execute(
                select(User).where(User.email == "jan.zahradnik@centrum.cz")
            )
            owner_user = result.scalars().first()

            if not owner_user:
                print("❌ Owner user not found")
                return False

            print(f"✅ Found owner: {owner_user.email}")

            # Get another user to share with
            result = await session.execute(
                select(User).where(User.email == "debug_member2@example.com")
            )
            target_user = result.scalars().first()

            if not target_user:
                print("❌ Target user not found")
                return False

            print(f"✅ Found target user: {target_user.email}")

            # Get the shopping list with items
            result = await session.execute(
                select(ShoppingList)
                .options(
                    selectinload(ShoppingList.items).selectinload(User),
                    selectinload(ShoppingList.shared_with),
                    selectinload(ShoppingList.owner),
                )
                .where(ShoppingList.id == 11)  # List with 26 items
            )
            shopping_list = result.scalars().first()

            if not shopping_list:
                print("❌ Shopping list not found")
                return False

            print(
                f"✅ Found shopping list: {shopping_list.name} with {len(shopping_list.items)} items"
            )

            # Test 1: Try to serialize the shopping list directly
            print("\n🧪 Test 1: Direct ShoppingListRead serialization")
            try:
                list_schema = ShoppingListRead.model_validate(
                    shopping_list, from_attributes=True
                )
                print("✅ ShoppingListRead validation successful")

                json_data = list_schema.model_dump(mode="json")
                print(f"✅ JSON serialization successful")
                print(f"   Items in serialized data: {len(json_data.get('items', []))}")

                # Check first item structure
                if json_data.get("items"):
                    first_item = json_data["items"][0]
                    print(f"   First item keys: {list(first_item.keys())}")

            except Exception as e:
                print(f"❌ Serialization failed: {e}")
                print(f"   Error type: {type(e).__name__}")
                import traceback

                traceback.print_exc()
                return False

            # Test 2: Test the actual share endpoint function
            print("\n🧪 Test 2: Share endpoint function call")
            try:
                share_data = ShareRequest(email=target_user.email)

                # Call the share function directly (simulating the endpoint)
                result = await share_shopping_list(
                    list_id=11,
                    share_data=share_data,
                    session=session,
                    current_user=owner_user,
                )

                print("✅ Share function completed successfully!")
                print(f"   Result type: {type(result)}")

                # Try to serialize the result
                result_schema = ShoppingListRead.model_validate(
                    result, from_attributes=True
                )
                result_json = result_schema.model_dump(mode="json")
                print(f"✅ Share result serialization successful")
                print(
                    f"   Members after sharing: {len(result_json.get('members', []))}"
                )

            except Exception as e:
                print(f"❌ Share function failed: {e}")
                print(f"   Error type: {type(e).__name__}")
                import traceback

                traceback.print_exc()
                return False

            return True

        except Exception as e:
            print(f"❌ Database error: {e}")
            import traceback

            traceback.print_exc()
            return False


if __name__ == "__main__":
    result = asyncio.run(test_share_serialization())
    if result:
        print("\n🎉 Share serialization test PASSED!")
        sys.exit(0)
    else:
        print("\n💥 Share serialization test FAILED!")
        sys.exit(1)
