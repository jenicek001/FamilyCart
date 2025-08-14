#!/usr/bin/env python3
"""
Test script to verify the invitation email functionality for non-existent users.
"""
import asyncio
import httpx
import json

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "nonexistent@example.com"

async def test_invitation_for_nonexistent_user():
    """Test sending invitation to non-existent user."""
    
    # First, get a token by logging in as a test user
    async with httpx.AsyncClient() as client:
        # Try to login with test user (from create_test_users.py)
        login_data = {
            "username": "debug_owner@example.com",
            "password": "TestPassword123!"
        }
        
        try:
            login_response = await client.post(
                f"{BASE_URL}/api/v1/auth/jwt/login",
                data=login_data
            )
            
            if login_response.status_code != 200:
                print(f"❌ Login failed: {login_response.status_code}")
                print(f"Response: {login_response.text}")
                return
                
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Get user's shopping lists
            lists_response = await client.get(
                f"{BASE_URL}/api/v1/shopping-lists",
                headers=headers
            )
            
            if lists_response.status_code != 200 or not lists_response.json():
                print("❌ No shopping lists found. Creating a test list first...")
                
                # Create a test list
                create_response = await client.post(
                    f"{BASE_URL}/api/v1/shopping-lists",
                    headers=headers,
                    json={"name": "Test List", "description": "Test list for invitation testing"}
                )
                
                if create_response.status_code != 200:
                    print(f"❌ Failed to create test list: {create_response.status_code}")
                    return
                    
                test_list = create_response.json()
            else:
                test_list = lists_response.json()[0]
            
            list_id = test_list["id"]
            print(f"📝 Using list: '{test_list['name']}' (ID: {list_id})")
            
            # Test sharing with non-existent user
            print(f"📧 Testing invitation to non-existent user: {TEST_EMAIL}")
            
            share_response = await client.post(
                f"{BASE_URL}/api/v1/shopping-lists/{list_id}/share",
                headers=headers,
                json={"email": TEST_EMAIL}
            )
            
            print(f"📊 Response status: {share_response.status_code}")
            
            if share_response.status_code == 200:
                print("✅ SUCCESS: Invitation sent successfully!")
                print("📧 Check the backend logs for email notification output")
                
                response_data = share_response.json()
                print(f"📋 List still has {len(response_data.get('members', []))} members (as expected)")
                
            elif share_response.status_code == 404:
                print("❌ STILL GETTING 404: The fix hasn't been applied yet")
                print(f"Response: {share_response.text}")
                
            elif share_response.status_code == 500:
                print("⚠️  500 ERROR: Email service might have failed")
                print(f"Response: {share_response.text}")
                
            else:
                print(f"❌ Unexpected status: {share_response.status_code}")
                print(f"Response: {share_response.text}")
                
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")

if __name__ == "__main__":
    print("🧪 Testing invitation functionality for non-existent users...")
    print("=" * 60)
    
    asyncio.run(test_invitation_for_nonexistent_user())
