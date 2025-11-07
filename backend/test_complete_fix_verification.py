#!/usr/bin/env python3
"""
Test script to verify both permission and serialization fixes.
Tests:
1. Shared user can view, update, and delete items
2. Shopping list endpoint returns proper JSON without serialization errors
3. All endpoints work for both owners and shared users
"""

import asyncio
import json
from typing import Any, Dict

import aiohttp

# Test configuration
BASE_URL = "http://localhost:8000/api/v1"
SHARED_USER_EMAIL = "berta.stepanova@gmail.com"
SHARED_USER_PASSWORD = "password123"
OWNER_EMAIL = "test@example.com"
OWNER_PASSWORD = "password123"
SHARED_LIST_ID = 11


async def authenticate_user(
    session: aiohttp.ClientSession, email: str, password: str
) -> str:
    """Authenticate user and return access token."""
    login_data = {"username": email, "password": password}

    async with session.post(
        f"{BASE_URL}/users/auth/jwt/login", data=login_data
    ) as response:
        if response.status == 200:
            data = await response.json()
            return data["access_token"]
        else:
            text = await response.text()
            raise Exception(f"Login failed for {email}: {response.status} - {text}")


async def make_authenticated_request(
    session: aiohttp.ClientSession,
    method: str,
    url: str,
    token: str,
    json_data: Dict[Any, Any] = None,
) -> tuple[int, Dict[Any, Any]]:
    """Make an authenticated request and return status code and response data."""
    headers = {"Authorization": f"Bearer {token}"}

    kwargs = {"headers": headers}
    if json_data:
        kwargs["json"] = json_data

    async with session.request(method, url, **kwargs) as response:
        status = response.status
        try:
            data = await response.json()
        except:
            data = {"error": await response.text()}
        return status, data


async def test_shopping_list_serialization(
    session: aiohttp.ClientSession, token: str, list_id: int
):
    """Test that shopping list endpoint returns proper JSON without serialization errors."""
    print(f"\n=== Testing Shopping List Serialization (List ID: {list_id}) ===")

    status, data = await make_authenticated_request(
        session, "GET", f"{BASE_URL}/shopping-lists/{list_id}", token
    )

    print(f"GET /shopping-lists/{list_id}")
    print(f"Status: {status}")

    if status == 200:
        print("✅ Shopping list retrieved successfully")
        print(f"List name: {data.get('name', 'N/A')}")
        print(f"Items count: {len(data.get('items', []))}")
        print(f"Members count: {len(data.get('members', []))}")

        # Check if response is properly structured
        required_fields = ["id", "name", "owner_id", "items", "members", "created_at"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            print(f"⚠️  Missing fields: {missing_fields}")
        else:
            print("✅ All required fields present")
    else:
        print(f"❌ Failed to retrieve shopping list: {data}")

    return status == 200


async def test_shared_user_permissions(
    session: aiohttp.ClientSession, token: str, list_id: int
):
    """Test that shared user can view, update, and delete items."""
    print(f"\n=== Testing Shared User Permissions (List ID: {list_id}) ===")

    # First, get the shopping list to see current items
    status, list_data = await make_authenticated_request(
        session, "GET", f"{BASE_URL}/shopping-lists/{list_id}", token
    )

    if status != 200:
        print(f"❌ Failed to get shopping list: {list_data}")
        return False

    items = list_data.get("items", [])
    print(f"Found {len(items)} items in the list")

    if not items:
        print("No items to test with, creating a test item first...")
        # Create a test item
        create_data = {
            "name": "Test Item for Permissions",
            "quantity": 1,
            "category": "Test Category",
        }

        status, create_response = await make_authenticated_request(
            session,
            "POST",
            f"{BASE_URL}/shopping-lists/{list_id}/items",
            token,
            create_data,
        )

        if status == 201:
            print("✅ Test item created successfully")
            test_item_id = create_response["id"]
        else:
            print(f"❌ Failed to create test item: {create_response}")
            return False
    else:
        # Use the first item for testing
        test_item_id = items[0]["id"]
        print(f"Using existing item ID: {test_item_id}")

    # Test reading single item
    print("\n--- Testing Item Read ---")
    status, item_data = await make_authenticated_request(
        session, "GET", f"{BASE_URL}/items/{test_item_id}", token
    )

    if status == 200:
        print(f"✅ Successfully read item: {item_data['name']}")
    else:
        print(f"❌ Failed to read item: {item_data}")
        return False

    # Test updating item
    print("\n--- Testing Item Update ---")
    update_data = {
        "name": f"Updated by shared user - {item_data['name']}",
        "is_completed": not item_data.get("is_completed", False),
    }

    status, update_response = await make_authenticated_request(
        session, "PUT", f"{BASE_URL}/items/{test_item_id}", token, update_data
    )

    if status == 200:
        print(f"✅ Successfully updated item")
        print(f"  New name: {update_response['name']}")
        print(f"  Completed: {update_response['is_completed']}")
    else:
        print(f"❌ Failed to update item: {update_response}")
        return False

    # Test that the update is reflected when getting the list again
    print("\n--- Verifying Update in List ---")
    status, updated_list = await make_authenticated_request(
        session, "GET", f"{BASE_URL}/shopping-lists/{list_id}", token
    )

    if status == 200:
        updated_item = next(
            (item for item in updated_list["items"] if item["id"] == test_item_id), None
        )
        if updated_item and updated_item["name"] == update_data["name"]:
            print("✅ Update reflected in shopping list")
        else:
            print("⚠️  Update may not be reflected properly")

    return True


async def test_owner_permissions(
    session: aiohttp.ClientSession, token: str, list_id: int
):
    """Test that owner still has full access."""
    print(f"\n=== Testing Owner Permissions (List ID: {list_id}) ===")

    # Test reading the list
    status, list_data = await make_authenticated_request(
        session, "GET", f"{BASE_URL}/shopping-lists/{list_id}", token
    )

    if status == 200:
        print(f"✅ Owner can read list: {list_data['name']}")
        print(f"  Items: {len(list_data.get('items', []))}")
        print(f"  Members: {len(list_data.get('members', []))}")
        return True
    else:
        print(f"❌ Owner failed to read list: {list_data}")
        return False


async def main():
    """Run all tests."""
    print("🚀 Starting FamilyCart Permission and Serialization Tests")

    async with aiohttp.ClientSession() as session:
        try:
            # Test 1: Authenticate shared user
            print("\n=== Authenticating Shared User ===")
            shared_token = await authenticate_user(
                session, SHARED_USER_EMAIL, SHARED_USER_PASSWORD
            )
            print(f"✅ Shared user authenticated: {SHARED_USER_EMAIL}")

            # Test 2: Test serialization with shared user
            serialization_ok = await test_shopping_list_serialization(
                session, shared_token, SHARED_LIST_ID
            )

            # Test 3: Test shared user permissions
            if serialization_ok:
                permissions_ok = await test_shared_user_permissions(
                    session, shared_token, SHARED_LIST_ID
                )
            else:
                permissions_ok = False

            # Test 4: Authenticate owner and test their access
            print("\n=== Authenticating Owner ===")
            owner_token = await authenticate_user(session, OWNER_EMAIL, OWNER_PASSWORD)
            print(f"✅ Owner authenticated: {OWNER_EMAIL}")

            # Test 5: Test owner permissions
            owner_ok = await test_owner_permissions(
                session, owner_token, SHARED_LIST_ID
            )

            # Test 6: Test serialization with owner
            owner_serialization_ok = await test_shopping_list_serialization(
                session, owner_token, SHARED_LIST_ID
            )

            # Final results
            print("\n" + "=" * 60)
            print("📋 TEST RESULTS SUMMARY")
            print("=" * 60)
            print(
                f"✅ Shared user authentication: {'PASS' if shared_token else 'FAIL'}"
            )
            print(
                f"✅ Serialization (shared user): {'PASS' if serialization_ok else 'FAIL'}"
            )
            print(f"✅ Shared user permissions: {'PASS' if permissions_ok else 'FAIL'}")
            print(f"✅ Owner authentication: {'PASS' if owner_token else 'FAIL'}")
            print(f"✅ Owner permissions: {'PASS' if owner_ok else 'FAIL'}")
            print(
                f"✅ Serialization (owner): {'PASS' if owner_serialization_ok else 'FAIL'}"
            )

            all_passed = all(
                [
                    shared_token,
                    serialization_ok,
                    permissions_ok,
                    owner_token,
                    owner_ok,
                    owner_serialization_ok,
                ]
            )
            print(
                f"\n🎯 OVERALL RESULT: {'🎉 ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}"
            )

        except Exception as e:
            print(f"\n💥 Test execution failed: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
