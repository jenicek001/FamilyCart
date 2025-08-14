#!/usr/bin/env python3
"""
Debug Sprint 5 Share Endpoint
"""

import asyncio
import httpx
import json


async def debug_share_endpoint():
    """Debug the share endpoint step by step."""
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        print("🔍 Debugging Sprint 5 Share Endpoint")
        print("=" * 40)
        
        # Test 1: Create user and get token
        print("\n1. Creating owner user...")
        owner_data = {
            "email": "debug_owner@example.com",
            "password": "TestPassword123!",
            "first_name": "Debug",
            "last_name": "Owner",
            "nickname": "DebugOwner"
        }
        
        response = await client.post(f"{base_url}/api/v1/auth/register", json=owner_data)
        if response.status_code == 400 and "REGISTER_USER_ALREADY_EXISTS" in response.text:
            print("✅ Owner user already exists, continuing...")
        elif response.status_code == 201:
            print("✅ Owner user created")
        else:
            print(f"❌ Owner creation failed: {response.status_code} - {response.text}")
            return
        
        # Login
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
            print("✅ Owner logged in")
        else:
            print(f"❌ Owner login failed: {response.status_code} - {response.text}")
            return
        
        # Test 2: Create member user  
        print("\n2. Creating member user...")
        member_data = {
            "email": "debug_member@example.com",
            "password": "TestPassword123!",
            "first_name": "Debug",
            "last_name": "Member",
            "nickname": "DebugMember"
        }
        
        response = await client.post(f"{base_url}/api/v1/auth/register", json=member_data)
        if response.status_code == 400 and "REGISTER_USER_ALREADY_EXISTS" in response.text:
            print("✅ Member user already exists")
        elif response.status_code == 201:
            print("✅ Member user created")
        else:
            print(f"❌ Member creation failed: {response.status_code} - {response.text}")
            return
        
        # Test 3: Create a shopping list
        print("\n3. Creating shopping list...")
        list_data = {"name": "Debug List"}
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
        
        # Test 4: Try to share with detailed error logging
        print(f"\n4. Testing share endpoint with list {list_id}...")
        share_data = {"email": member_data["email"]}
        
        try:
            response = await client.post(
                f"{base_url}/api/v1/shopping-lists/{list_id}/share",
                json=share_data,
                headers=owner_headers
            )
            
            print(f"Status: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Share successful!")
                print(f"Shared list: {result.get('name')}")
                print(f"Members count: {len(result.get('members', []))}")
            else:
                print(f"❌ Share failed: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception during share: {e}")


if __name__ == "__main__":
    asyncio.run(debug_share_endpoint())
