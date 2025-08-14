#!/usr/bin/env python3
"""
Create a test user with a known password for testing
"""
import asyncio
import httpx
import json

async def create_test_user():
    base_url = "http://localhost:8000"
    
    # User data with known password
    user_data = {
        "email": "sharetest@example.com",
        "password": "ShareTest123!",
        "full_name": "Share Test User",
        "nickname": "ShareTester"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{base_url}/api/v1/auth/register",
                json=user_data
            )
            
            if response.status_code == 201:
                user = response.json()
                print(f"✅ Created test user: {user['email']}")
                
                # Now login to verify credentials work
                login_response = await client.post(
                    f"{base_url}/api/v1/auth/jwt/login",
                    data={"username": user_data["email"], "password": user_data["password"]},
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                
                if login_response.status_code == 200:
                    token_data = login_response.json()
                    print(f"✅ Login successful, token: {token_data['access_token'][:50]}...")
                    
                    # Create a shopping list for testing
                    list_data = {
                        "name": "Share Test List",
                        "description": "List for testing share endpoint"
                    }
                    
                    list_response = await client.post(
                        f"{base_url}/api/v1/shopping-lists/",
                        json=list_data,
                        headers={"Authorization": f"Bearer {token_data['access_token']}"}
                    )
                    
                    if list_response.status_code == 201:
                        shopping_list = list_response.json()
                        print(f"✅ Created shopping list: {shopping_list['id']} - {shopping_list['name']}")
                        return user_data["email"], user_data["password"], shopping_list["id"]
                    else:
                        print(f"❌ Failed to create shopping list: {list_response.status_code}")
                        print(f"Response: {await list_response.text()}")
                else:
                    print(f"❌ Login failed: {login_response.status_code}")
                    print(f"Response: {await login_response.text()}")
            else:
                print(f"❌ Failed to create user: {response.status_code}")
                print(f"Response: {await response.text()}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return None, None, None

if __name__ == "__main__":
    email, password, list_id = asyncio.run(create_test_user())
    if email:
        print(f"\n📋 Test credentials:")
        print(f"Email: {email}")
        print(f"Password: {password}")
        print(f"Shopping List ID: {list_id}")
