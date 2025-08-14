#!/usr/bin/env python3
"""
Simple synchronous test for the share endpoint
"""
import requests
import json

def test_share_endpoint_simple():
    base_url = "http://localhost:8000"
    
    # Step 1: Login
    print("🔑 Logging in...")
    login_data = {
        "username": "debug_owner@example.com",
        "password": "TestPassword123!"
    }
    
    login_response = requests.post(
        f"{base_url}/api/v1/auth/jwt/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    print(f"Login status: {login_response.status_code}")
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.text}")
        return
    
    login_result = login_response.json()
    token = login_result["access_token"]
    print(f"✅ Login successful")
    
    # Step 2: Get shopping lists
    print("\n📋 Getting shopping lists...")
    lists_response = requests.get(
        f"{base_url}/api/v1/shopping-lists/",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"Lists status: {lists_response.status_code}")
    if lists_response.status_code != 200:
        print(f"Failed to get lists: {lists_response.text}")
        return
    
    lists = lists_response.json()
    if not lists:
        print("No shopping lists found")
        return
    
    list_id = lists[0]["id"]
    print(f"✅ Using shopping list ID: {list_id}")
    
    # Step 3: Test sharing with existing user
    print("\n🤝 Testing share with existing user...")
    share_data = {"email": "debug_member@example.com"}
    
    share_response = requests.post(
        f"{base_url}/api/v1/shopping-lists/{list_id}/share",
        json=share_data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    )
    
    print(f"Share status: {share_response.status_code}")
    if share_response.status_code == 200:
        print("✅ Share with existing user SUCCESS! Serialization issue is FIXED!")
        result = share_response.json()
        print(f"Response contains {len(result.get('items', []))} items and {len(result.get('members', []))} members")
    else:
        print(f"❌ Share failed: {share_response.status_code}")
        print(f"Response: {share_response.text}")
        return
    
    # Step 4: Test sharing with non-existent user
    print("\n👻 Testing share with non-existent user...")
    share_data_nonexistent = {"email": "nonexistent@example.com"}
    
    share_response_nonexistent = requests.post(
        f"{base_url}/api/v1/shopping-lists/{list_id}/share",
        json=share_data_nonexistent,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    )
    
    print(f"Non-existent user share status: {share_response_nonexistent.status_code}")
    if share_response_nonexistent.status_code == 200:
        print("✅ Share with non-existent user SUCCESS!")
        result = share_response_nonexistent.json()
        print(f"Response contains {len(result.get('items', []))} items and {len(result.get('members', []))} members")
    else:
        print(f"❌ Non-existent user share failed: {share_response_nonexistent.status_code}")
        print(f"Response: {share_response_nonexistent.text}")

if __name__ == "__main__":
    test_share_endpoint_simple()
