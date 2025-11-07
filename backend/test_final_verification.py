#!/usr/bin/env python3
"""
Final verification test for FamilyCart backend fixes.
Tests all endpoints for both owners and shared users.
"""

import asyncio
import json
import sys

import aiohttp

# Test configuration
BASE_URL = "http://localhost:8000"
OWNER_EMAIL = "jan.zahradnik@centrum.cz"
OWNER_PASSWORD = "bagr123"
SHARED_EMAIL = "berta.stepanova@gmail.com"
SHARED_PASSWORD = "berta"


class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = None
        self.token = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def login(self, email: str, password: str):
        """Login and store token"""
        data = {"username": email, "password": password}
        async with self.session.post(
            f"{self.base_url}/api/v1/auth/jwt/login", data=data
        ) as resp:
            if resp.status == 200:
                result = await resp.json()
                self.token = result["access_token"]
                print(f"✓ Logged in as {email}")
                return True
            else:
                text = await resp.text()
                print(f"✗ Login failed for {email}: {resp.status} - {text}")
                return False

    async def request(self, method: str, endpoint: str, **kwargs):
        """Make authenticated request"""
        headers = kwargs.get("headers", {})
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        kwargs["headers"] = headers

        url = f"{self.base_url}{endpoint}"
        async with self.session.request(method, url, **kwargs) as resp:
            try:
                data = await resp.json()
            except:
                data = await resp.text()
            return resp.status, data


async def test_shopping_list_endpoints():
    """Test shopping list endpoints for both owner and shared user"""
    print("🧪 Testing shopping list endpoints...")

    # Test data
    list_data = {
        "name": "Test Verification List",
        "description": "Final verification test list",
    }

    async with APIClient(BASE_URL) as owner_client:
        # Owner login
        if not await owner_client.login(OWNER_EMAIL, OWNER_PASSWORD):
            print("❌ Owner login failed")
            return False

        # Create shopping list
        status, data = await owner_client.request(
            "POST", "/api/v1/shopping-lists/", json=list_data
        )
        if status != 200:
            print(f"❌ Create list failed: {status} - {data}")
            return False

        list_id = data["id"]
        print(f"✓ Created list with ID: {list_id}")

        # Share list with shared user
        share_data = {"email": SHARED_EMAIL}
        status, data = await owner_client.request(
            "POST", f"/api/v1/shopping-lists/{list_id}/share", json=share_data
        )
        if status != 200:
            print(f"❌ Share list failed: {status} - {data}")
            return False
        print("✓ Shared list successfully")

        # Owner: Get specific list
        status, data = await owner_client.request(
            "GET", f"/api/v1/shopping-lists/{list_id}"
        )
        if status != 200:
            print(f"❌ Owner get list failed: {status} - {data}")
            return False
        print("✓ Owner can get list")

        # Owner: Add item to list
        item_data = {
            "name": "Test Item",
            "quantity": 2,
            "description": "Test item for verification",
        }
        status, item_response = await owner_client.request(
            "POST", f"/api/v1/shopping-lists/{list_id}/items", json=item_data
        )
        if status != 200:
            print(f"❌ Owner add item failed: {status} - {item_response}")
            return False

        item_id = item_response["id"]
        print(f"✓ Owner added item with ID: {item_id}")

    # Test shared user access
    async with APIClient(BASE_URL) as shared_client:
        # Shared user login
        if not await shared_client.login(SHARED_EMAIL, SHARED_PASSWORD):
            print("❌ Shared user login failed")
            return False

        # Shared user: Get specific list
        status, data = await shared_client.request(
            "GET", f"/api/v1/shopping-lists/{list_id}"
        )
        if status != 200:
            print(f"❌ Shared user get list failed: {status} - {data}")
            return False
        print("✓ Shared user can get list")

        # Shared user: Get items from list
        status, data = await shared_client.request(
            "GET", f"/api/v1/shopping-lists/{list_id}/items"
        )
        if status != 200:
            print(f"❌ Shared user get items failed: {status} - {data}")
            return False
        print("✓ Shared user can get items")

        # Shared user: Update item
        update_data = {"is_completed": True}
        status, data = await shared_client.request(
            "PUT", f"/api/v1/items/{item_id}", json=update_data
        )
        if status != 200:
            print(f"❌ Shared user update item failed: {status} - {data}")
            return False
        print("✓ Shared user can update item")

        # Shared user: Get specific item
        status, data = await shared_client.request("GET", f"/api/v1/items/{item_id}")
        if status != 200:
            print(f"❌ Shared user get item failed: {status} - {data}")
            return False
        print("✓ Shared user can get specific item")

        # Shared user: Add item to list
        shared_item_data = {
            "name": "Shared User Item",
            "quantity": 1,
            "description": "Item added by shared user",
        }
        status, data = await shared_client.request(
            "POST", f"/api/v1/shopping-lists/{list_id}/items", json=shared_item_data
        )
        if status != 200:
            print(f"❌ Shared user add item failed: {status} - {data}")
            return False

        shared_item_id = data["id"]
        print(f"✓ Shared user added item with ID: {shared_item_id}")

        # Shared user: Delete their item
        status, data = await shared_client.request(
            "DELETE", f"/api/v1/items/{shared_item_id}"
        )
        if status != 200:
            print(f"❌ Shared user delete item failed: {status} - {data}")
            return False
        print("✓ Shared user can delete item")

    # Cleanup: Owner deletes the list
    async with APIClient(BASE_URL) as owner_client:
        await owner_client.login(OWNER_EMAIL, OWNER_PASSWORD)
        status, data = await owner_client.request(
            "DELETE", f"/api/v1/shopping-lists/{list_id}"
        )
        if status != 204:
            print(f"⚠️ Cleanup failed: {status} - {data}")
        else:
            print("✓ Cleanup completed")

    return True


async def test_serialization_issues():
    """Test endpoints that previously had serialization issues"""
    print("\n🔧 Testing serialization fixes...")

    async with APIClient(BASE_URL) as client:
        # Login as owner
        if not await client.login(OWNER_EMAIL, OWNER_PASSWORD):
            return False

        # Get all lists (this endpoint had serialization issues)
        status, data = await client.request("GET", "/api/v1/shopping-lists/")
        if status != 200:
            print(f"❌ Get all lists failed: {status} - {data}")
            return False
        print("✓ Get all lists works (no serialization error)")

        # Create a list and immediately get it (tests serialization consistency)
        list_data = {
            "name": "Serialization Test",
            "description": "Test for serialization",
        }
        status, create_response = await client.request(
            "POST", "/api/v1/shopping-lists/", json=list_data
        )
        if status != 200:
            print(f"❌ Create list failed: {status} - {create_response}")
            return False

        list_id = create_response["id"]

        # Get the created list
        status, get_response = await client.request(
            "GET", f"/api/v1/shopping-lists/{list_id}"
        )
        if status != 200:
            print(f"❌ Get created list failed: {status} - {get_response}")
            return False
        print("✓ Create and get list works (no serialization error)")

        # Add item and get list (tests complex serialization)
        item_data = {"name": "Serialization Test Item", "quantity": 1}
        status, item_response = await client.request(
            "POST", f"/api/v1/shopping-lists/{list_id}/items", json=item_data
        )
        if status != 200:
            print(f"❌ Add item failed: {status} - {item_response}")
            return False

        # Get list with items
        status, list_with_items = await client.request(
            "GET", f"/api/v1/shopping-lists/{list_id}"
        )
        if status != 200:
            print(f"❌ Get list with items failed: {status} - {list_with_items}")
            return False
        print("✓ Get list with items works (no serialization error)")

        # Share and get (this was the main problematic endpoint)
        share_data = {"email": SHARED_EMAIL}
        status, share_response = await client.request(
            "POST", f"/api/v1/shopping-lists/{list_id}/share", json=share_data
        )
        if status != 200:
            print(f"❌ Share list failed: {status} - {share_response}")
            return False
        print("✓ Share list works (no serialization error)")

        # Cleanup
        await client.request("DELETE", f"/api/v1/shopping-lists/{list_id}")

    return True


async def main():
    """Run all verification tests"""
    print("🚀 Starting final verification tests for FamilyCart backend fixes\n")

    # Test endpoints functionality
    success1 = await test_shopping_list_endpoints()

    # Test serialization fixes
    success2 = await test_serialization_issues()

    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 ALL TESTS PASSED! The backend fixes are working correctly.")
        print("✅ Serialization issues resolved")
        print("✅ Permission issues resolved")
        print("✅ Both owners and shared users can access all endpoints")
        return 0
    else:
        print("❌ SOME TESTS FAILED! Please check the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
