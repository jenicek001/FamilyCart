#!/usr/bin/env python3
"""
Test script to reproduce the issue where Berta (shared user) 
cannot delete items from Honzík's (owner) shopping list.

Usage: poetry run python test_shared_user_delete.py
"""

import requests
import json
import sys

def test_shared_user_item_deletion():
    """Test that shared users can delete items from owner's list"""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Shared User Item Deletion Issue")
    print("=" * 50)
    
    # Step 1: Login as Berta (shared user)
    print("📋 Step 1: Login as Berta (shared user)")
    login_data = {
        "username": "berta.stepanova@gmail.com",
        "password": "berta"
    }
    
    login_response = requests.post(
        f"{base_url}/api/v1/auth/jwt/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    print(f"Login status: {login_response.status_code}")
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return False
    
    login_result = login_response.json()
    berta_token = login_result["access_token"]
    
    print("✅ Berta login successful")
    
    # Step 2: Get Berta's shopping lists (should include shared lists)
    print("📋 Step 2: Get Berta's accessible shopping lists")
    headers = {"Authorization": f"Bearer {berta_token}"}
    
    lists_response = requests.get(f"{base_url}/api/v1/shopping-lists", headers=headers)
    print(f"Lists fetch status: {lists_response.status_code}")
    
    if lists_response.status_code != 200:
        print(f"❌ Failed to fetch lists: {lists_response.text}")
        return False
    
    lists_data = lists_response.json()
    print(f"✅ Berta can see {len(lists_data)} shopping lists")
    
    # Find a list that Berta doesn't own (shared list)
    shared_list = None
    for list_item in lists_data:
        print(f"  - List {list_item['id']}: {list_item['name']} (owner: {list_item.get('owner_email', 'N/A')})")
        if list_item.get('owner_email') != 'berta.stepanova@gmail.com':
            shared_list = list_item
            break
    
    if not shared_list:
        print("❌ No shared lists found for Berta")
        return False
    
    list_id = shared_list['id']
    print(f"✅ Found shared list: {shared_list['name']} (ID: {list_id})")
    
    # Step 3: Get items from the shared list
    print("📋 Step 3: Get items from the shared list")
    
    # First try to get list details with items
    list_detail_response = requests.get(f"{base_url}/api/v1/shopping-lists/{list_id}", headers=headers)
    print(f"List detail status: {list_detail_response.status_code}")
    
    if list_detail_response.status_code != 200:
        print(f"❌ Failed to get list details: {list_detail_response.text}")
        return False
    
    list_detail = list_detail_response.json()
    items = list_detail.get('items', [])
    print(f"✅ Found {len(items)} items in the shared list")
    
    if not items:
        # Add a test item first
        print("📋 Step 3.1: Adding a test item to delete")
        new_item_data = {
            "name": "Test item for deletion",
            "quantity": 1
        }
        
        add_response = requests.post(
            f"{base_url}/api/v1/shopping-lists/{list_id}/items",
            json=new_item_data,
            headers=headers
        )
        
        print(f"Add item status: {add_response.status_code}")
        if add_response.status_code not in [200, 201]:
            print(f"❌ Failed to add test item: {add_response.text}")
            return False
        
        added_item = add_response.json()
        item_id = added_item['id']
        print(f"✅ Added test item with ID: {item_id}")
    else:
        # Use the first existing item
        item_id = items[0]['id']
        print(f"✅ Will try to delete existing item with ID: {item_id} ('{items[0]['name']}')")
    
    # Step 4: Try to delete the item as Berta
    print("📋 Step 4: Attempt to delete item as Berta (shared user)")
    
    delete_response = requests.delete(f"{base_url}/api/v1/items/{item_id}", headers=headers)
    print(f"Delete status: {delete_response.status_code}")
    
    if delete_response.status_code == 500:
        print(f"❌ 500 Server Error when deleting item: {delete_response.text}")
        print("This confirms the bug - shared users get 500 error when deleting items")
        return False
    elif delete_response.status_code == 403:
        print(f"❌ 403 Permission Error when deleting item: {delete_response.text}")
        print("Permission logic is incorrectly blocking shared users")
        return False
    elif delete_response.status_code == 200:
        print("✅ Item deleted successfully!")
        result = delete_response.json()
        print(f"Delete result: {result}")
        return True
    else:
        print(f"❌ Unexpected status code {delete_response.status_code}: {delete_response.text}")
        return False

if __name__ == "__main__":
    success = test_shared_user_item_deletion()
    
    if success:
        print("\n✅ Test passed - shared user can delete items!")
        sys.exit(0)
    else:
        print("\n❌ Test failed - there's a bug with shared user item deletion!")
        sys.exit(1)
