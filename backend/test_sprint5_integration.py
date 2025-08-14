#!/usr/bin/env python3
"""
Manual Sprint 5 Integration Test Script
Tests the actual API endpoints for sharing functionality.
"""

import asyncio
import httpx
import json


async def test_sprint5_sharing_integration():
    """Test Sprint 5 sharing functionality with real API calls."""
    
    import time
    import random
    
    # Generate unique identifiers to avoid conflicts with existing users
    timestamp = int(time.time())
    rand_id = random.randint(1000, 9999)
    unique_suffix = f"{timestamp}_{rand_id}"
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        print("🧪 Testing Sprint 5: List Sharing & Collaboration")
        print("=" * 50)
        
        # Step 1: Register two test users
        print("\n1. Creating test users...")
        
        # User 1 (owner)
        owner_data = {
            "email": f"owner_test_{unique_suffix}@example.com",
            "password": "TestPassword123!",
            "first_name": "Owner",
            "last_name": "User",
            "nickname": f"OwnerUser_{unique_suffix}"
        }
        
        response = await client.post(f"{base_url}/api/v1/auth/register", json=owner_data)
        if response.status_code == 201:
            print("✅ Owner user created successfully")
        else:
            print(f"❌ Owner creation failed: {response.status_code} - {response.text}")
            return
        
        # User 2 (member)
        member_data = {
            "email": f"member_test_{unique_suffix}@example.com", 
            "password": "TestPassword123!",
            "first_name": "Member",
            "last_name": "User",
            "nickname": f"MemberUser_{unique_suffix}"
        }
        
        response = await client.post(f"{base_url}/api/v1/auth/register", json=member_data)
        if response.status_code == 201:
            print("✅ Member user created successfully")
        else:
            print(f"❌ Member creation failed: {response.status_code} - {response.text}")
            return
        
        # Step 2: Login users to get tokens
        print("\n2. Logging in users...")
        
        # Login owner
        owner_login = {
            "username": owner_data["email"],
            "password": owner_data["password"]
        }
        response = await client.post(
            f"{base_url}/api/v1/auth/jwt/login",
            data=owner_login,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            owner_token = response.json()["access_token"]
            owner_headers = {"Authorization": f"Bearer {owner_token}"}
            print("✅ Owner logged in successfully")
        else:
            print(f"❌ Owner login failed: {response.status_code} - {response.text}")
            return
        
        # Login member
        member_login = {
            "username": member_data["email"],
            "password": member_data["password"]
        }
        response = await client.post(
            f"{base_url}/api/v1/auth/jwt/login",
            data=member_login,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            member_token = response.json()["access_token"]
            member_headers = {"Authorization": f"Bearer {member_token}"}
            print("✅ Member logged in successfully")
        else:
            print(f"❌ Member login failed: {response.status_code} - {response.text}")
            return
        
        # Step 3: Owner creates a shopping list
        print("\n3. Creating shopping list...")
        
        list_data = {"name": "Shared Grocery List"}
        response = await client.post(
            f"{base_url}/api/v1/shopping-lists",
            json=list_data,
            headers=owner_headers
        )
        
        if response.status_code == 200:
            shopping_list = response.json()
            list_id = shopping_list["id"]
            print(f"✅ Shopping list created: ID {list_id}")
        else:
            print(f"❌ List creation failed: {response.status_code} - {response.text}")
            return
        
        # Step 4: Test sharing the list
        print("\n4. Sharing list with member...")
        
        share_data = {"email": member_data["email"]}
        response = await client.post(
            f"{base_url}/api/v1/shopping-lists/{list_id}/share",
            json=share_data,
            headers=owner_headers
        )
        
        if response.status_code == 200:
            print("✅ List shared successfully")
        else:
            print(f"❌ List sharing failed: {response.status_code} - {response.text}")
            return
        
        # Step 5: Test member can access the shared list
        print("\n5. Testing member access to shared list...")
        
        response = await client.get(
            f"{base_url}/api/v1/shopping-lists/{list_id}",
            headers=member_headers
        )
        
        if response.status_code == 200:
            shared_list = response.json()
            print(f"✅ Member can access shared list: {shared_list['name']}")
        else:
            print(f"❌ Member access failed: {response.status_code} - {response.text}")
            return
        
        # Step 6: Test member can add items to shared list
        print("\n6. Testing member can add items...")
        
        item_data = {"name": "Milk", "quantity": "1L"}
        response = await client.post(
            f"{base_url}/api/v1/shopping-lists/{list_id}/items",
            json=item_data,
            headers=member_headers
        )
        
        if response.status_code == 200:
            item = response.json()
            print(f"✅ Member added item: {item['name']}")
        else:
            print(f"❌ Item creation by member failed: {response.status_code} - {response.text}")
            return
        
        # Step 7: Test owner can see member's items
        print("\n7. Testing owner can see member's items...")
        
        response = await client.get(
            f"{base_url}/api/v1/shopping-lists/{list_id}/items",
            headers=owner_headers
        )
        
        if response.status_code == 200:
            items = response.json()
            if items and len(items) > 0:
                print(f"✅ Owner can see {len(items)} item(s) including member's additions")
            else:
                print("⚠️ No items found in shared list")
        else:
            print(f"❌ Owner item access failed: {response.status_code} - {response.text}")
            return
        
        # Step 8: Test unauthorized user cannot access list
        print("\n8. Testing unauthorized access protection...")
        
        # Create third user (unauthorized)
        outsider_data = {
            "email": f"outsider_test_{unique_suffix}@example.com",
            "password": "TestPassword123!",
            "first_name": "Outsider",
            "last_name": "User", 
            "nickname": f"OutsiderUser_{unique_suffix}"
        }
        
        response = await client.post(f"{base_url}/api/v1/auth/register", json=outsider_data)
        if response.status_code != 201:
            print(f"❌ Outsider creation failed: {response.status_code}")
            return
            
        # Login outsider
        outsider_login = {
            "username": outsider_data["email"],
            "password": outsider_data["password"]
        }
        response = await client.post(
            f"{base_url}/api/v1/auth/jwt/login",
            data=outsider_login,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code != 200:
            print(f"❌ Outsider login failed: {response.status_code}")
            return
            
        outsider_token = response.json()["access_token"]
        outsider_headers = {"Authorization": f"Bearer {outsider_token}"}
        
        # Try to access list as outsider
        response = await client.get(
            f"{base_url}/api/v1/shopping-lists/{list_id}",
            headers=outsider_headers
        )
        
        if response.status_code == 403:
            print("✅ Unauthorized access properly blocked (403)")
        else:
            print(f"❌ Security issue: Outsider access not blocked properly: {response.status_code}")
            return
        
        print("\n" + "=" * 50)
        print("🎉 Sprint 5 Integration Test PASSED!")
        print("✅ All sharing and collaboration features working correctly")


if __name__ == "__main__":
    asyncio.run(test_sprint5_sharing_integration())
