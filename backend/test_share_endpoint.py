#!/usr/bin/env python3
"""
Test script to verify that the share endpoint works correctly for existing users.
"""
import asyncio
import aiohttp
import json

async def test_share_endpoint():
    """Test sharing a shopping list with an existing user"""
    base_url = "http://localhost:8000"
    
    # Test data - using known test users
    login_data = {
        "email": "test1@example.com",
        "password": "testpassword123"
    }
    
    share_data = {
        "email": "test2@example.com"  # Share with another test user
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            # Step 1: Login to get auth token
            print("🔐 Logging in...")
            async with session.post(f"{base_url}/api/v1/auth/jwt/login", data=login_data) as response:
                if response.status != 200:
                    print(f"❌ Login failed: {response.status}")
                    text = await response.text()
                    print(f"   Response: {text}")
                    return False
                
                # Get token from cookies or response
                auth_header = None
                if 'Set-Cookie' in response.headers:
                    cookies = response.headers['Set-Cookie']
                    print(f"✅ Login successful, got cookies")
                    # For cookie-based auth, we'll use the session cookies
                else:
                    # Try to get token from response body (if using JWT)
                    try:
                        response_data = await response.json()
                        if 'access_token' in response_data:
                            auth_header = f"Bearer {response_data['access_token']}"
                            print(f"✅ Login successful, got token")
                    except:
                        print("✅ Login successful (cookie-based)")
            
            # Step 2: Get user's shopping lists
            print("📋 Getting shopping lists...")
            headers = {}
            if auth_header:
                headers['Authorization'] = auth_header
                
            async with session.get(f"{base_url}/api/v1/shopping-lists/", headers=headers) as response:
                if response.status != 200:
                    print(f"❌ Failed to get shopping lists: {response.status}")
                    text = await response.text()
                    print(f"   Response: {text}")
                    return False
                
                lists = await response.json()
                if not lists:
                    print("❌ No shopping lists found")
                    return False
                
                first_list = lists[0]
                list_id = first_list['id']
                print(f"✅ Found shopping list: {first_list['name']} (ID: {list_id})")
            
            # Step 3: Try to share the list
            print(f"🤝 Sharing list {list_id} with {share_data['email']}...")
            async with session.post(
                f"{base_url}/api/v1/shopping-lists/{list_id}/share",
                headers={**headers, 'Content-Type': 'application/json'},
                data=json.dumps(share_data)
            ) as response:
                print(f"📡 Share request status: {response.status}")
                
                if response.status == 200:
                    print("✅ Share request successful!")
                    response_data = await response.json()
                    print(f"   Shared list has {len(response_data.get('items', []))} items")
                    print(f"   List members: {len(response_data.get('members', []))}")
                    return True
                else:
                    print(f"❌ Share request failed: {response.status}")
                    text = await response.text()
                    print(f"   Response: {text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Error during test: {e}")
            return False

if __name__ == "__main__":
    success = asyncio.run(test_share_endpoint())
    if success:
        print("\n🎉 Share endpoint test PASSED!")
    else:
        print("\n💥 Share endpoint test FAILED!")
