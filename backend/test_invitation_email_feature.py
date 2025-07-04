#!/usr/bin/env python3
"""
Test script to verify the new invitation email functionality for non-existent users.
This test verifies that sharing with non-existent users sends invitation emails
instead of returning 404 errors.
"""

import asyncio
import httpx
import json
from typing import Dict, Any

# Test configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# Test user credentials (assuming these exist in the database)
TEST_USER = {
    "email": "test@example.com",
    "password": "testpassword123"
}

# Non-existent user email for testing invitation
NON_EXISTENT_EMAIL = "nonexistent.user@example.com"


async def login_user(client: httpx.AsyncClient, email: str, password: str) -> str:
    """Login and return the access token."""
    login_data = {
        "username": email,  # FastAPI users expects username field
        "password": password
    }
    
    response = await client.post(
        f"{API_BASE}/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code != 200:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None
    
    # Extract token from response
    token_data = response.json()
    return token_data.get("access_token")


async def create_test_shopping_list(client: httpx.AsyncClient, token: str) -> int:
    """Create a test shopping list and return its ID."""
    list_data = {
        "name": "Test Invitation List",
        "description": "List for testing invitation email functionality"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.post(
        f"{API_BASE}/shopping-lists/",
        json=list_data,
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"Failed to create shopping list: {response.status_code} - {response.text}")
        return None
    
    list_info = response.json()
    print(f"✅ Created test shopping list: {list_info['name']} (ID: {list_info['id']})")
    return list_info["id"]


async def test_share_with_nonexistent_user(client: httpx.AsyncClient, token: str, list_id: int) -> bool:
    """Test sharing with a non-existent user - should send invitation email."""
    share_data = {
        "email": NON_EXISTENT_EMAIL
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.post(
        f"{API_BASE}/shopping-lists/{list_id}/share",
        json=share_data,
        headers=headers
    )
    
    print(f"\n🧪 Testing share with non-existent user: {NON_EXISTENT_EMAIL}")
    print(f"Response status: {response.status_code}")
    print(f"Response content: {response.text}")
    
    if response.status_code == 200:
        print("✅ SUCCESS: Share endpoint returned 200 (invitation email should be sent)")
        return True
    elif response.status_code == 404:
        print("❌ FAILURE: Still getting 404 error - old behavior")
        return False
    else:
        print(f"❌ UNEXPECTED: Got status {response.status_code}")
        return False


async def test_share_with_existing_user(client: httpx.AsyncClient, token: str, list_id: int) -> bool:
    """Test sharing with an existing user - should work normally."""
    share_data = {
        "email": TEST_USER["email"]  # Share with self (existing user)
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.post(
        f"{API_BASE}/shopping-lists/{list_id}/share",
        json=share_data,
        headers=headers
    )
    
    print(f"\n🧪 Testing share with existing user: {TEST_USER['email']}")
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ SUCCESS: Share with existing user works")
        return True
    else:
        print(f"❌ FAILURE: Expected 200, got {response.status_code}")
        return False


async def cleanup_test_list(client: httpx.AsyncClient, token: str, list_id: int):
    """Clean up the test shopping list."""
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.delete(
        f"{API_BASE}/shopping-lists/{list_id}",
        headers=headers
    )
    
    if response.status_code == 204:
        print(f"✅ Cleaned up test shopping list (ID: {list_id})")
    else:
        print(f"⚠️  Failed to clean up test list: {response.status_code}")


async def main():
    """Main test function."""
    print("🚀 Testing Invitation Email Feature for Non-Existent Users")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        # Step 1: Login
        print("1. Logging in...")
        token = await login_user(client, TEST_USER["email"], TEST_USER["password"])
        if not token:
            print("❌ Login failed. Make sure the test user exists and the backend is running.")
            return
        print("✅ Login successful")
        
        # Step 2: Create test shopping list
        print("\n2. Creating test shopping list...")
        list_id = await create_test_shopping_list(client, token)
        if not list_id:
            print("❌ Failed to create test shopping list")
            return
        
        # Step 3: Test sharing with non-existent user (main test case)
        success_nonexistent = await test_share_with_nonexistent_user(client, token, list_id)
        
        # Step 4: Test sharing with existing user (control test)
        success_existing = await test_share_with_existing_user(client, token, list_id)
        
        # Step 5: Cleanup
        print("\n5. Cleaning up...")
        await cleanup_test_list(client, token, list_id)
        
        # Results
        print("\n" + "=" * 60)
        print("🏁 TEST RESULTS:")
        print(f"   Non-existent user invitation: {'✅ PASS' if success_nonexistent else '❌ FAIL'}")
        print(f"   Existing user sharing: {'✅ PASS' if success_existing else '❌ FAIL'}")
        
        if success_nonexistent and success_existing:
            print("\n🎉 ALL TESTS PASSED! Invitation email feature is working correctly.")
        else:
            print("\n💥 SOME TESTS FAILED. Check the implementation.")
        
        print("\n📧 Note: Check the backend logs to see if invitation emails are being sent.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
