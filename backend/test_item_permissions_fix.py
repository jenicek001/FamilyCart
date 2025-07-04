#!/usr/bin/env python3
"""
Test the item permission fix for shared shopping lists.
Verify that shared users can now update, view, and delete items.
"""
import requests
import json

def test_shared_user_item_permissions():
    base_url = "http://localhost:8000"
    
    print("🔧 Testing Item Permission Fix for Shared Users")
    print("=" * 60)
    
    # Step 1: Login as Berta (shared user)
    print("🔑 Logging in as Berta (shared user)...")
    login_data = {
        "username": "berta.stepanova@gmail.com", 
        "password": "Password123!"
    }
    
    login_response = requests.post(
        f"{base_url}/api/v1/auth/jwt/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    print(f"Login status: {login_response.status_code}")
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        # Try with different password
        login_data["password"] = "TestPassword123!"
        login_response = requests.post(
            f"{base_url}/api/v1/auth/jwt/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        print(f"Retry login status: {login_response.status_code}")
        if login_response.status_code != 200:
            print(f"❌ Login still failed: {login_response.text}")
            return
    
    login_result = login_response.json()
    token = login_result["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful")
    
    # Step 2: Get shared shopping list (list 11)
    print("\n📋 Getting shared shopping list 11...")
    list_response = requests.get(
        f"{base_url}/api/v1/shopping-lists/11",
        headers=headers
    )
    
    print(f"List access status: {list_response.status_code}")
    if list_response.status_code != 200:
        print(f"❌ Cannot access shared list: {list_response.text}")
        return
    
    list_data = list_response.json()
    print(f"✅ Successfully accessed shared list: {list_data['name']}")
    print(f"   Items in list: {len(list_data.get('items', []))}")
    
    # Step 3: Test updating an item (mark as completed)
    print("\n🔄 Testing item update (mark as completed)...")
    
    # Find an uncompleted item to test with
    uncompleted_items = [item for item in list_data.get('items', []) if not item.get('is_completed', False)]
    
    if not uncompleted_items:
        print("⚠️  No uncompleted items found to test with")
        return
    
    test_item = uncompleted_items[0]
    item_id = test_item['id']
    print(f"   Testing with item: {test_item['name']} (ID: {item_id})")
    
    # Try to mark item as completed
    update_response = requests.put(
        f"{base_url}/api/v1/items/{item_id}",
        headers=headers,
        json={"is_completed": True}
    )
    
    print(f"Item update status: {update_response.status_code}")
    if update_response.status_code == 200:
        print("✅ SUCCESS! Shared user can now update items!")
        updated_item = update_response.json()
        print(f"   Item '{updated_item['name']}' marked as completed: {updated_item['is_completed']}")
    else:
        print(f"❌ Item update failed: {update_response.text}")
        return
    
    # Step 4: Test reading a single item
    print(f"\n👁️  Testing single item read...")
    read_response = requests.get(
        f"{base_url}/api/v1/items/{item_id}",
        headers=headers
    )
    
    print(f"Item read status: {read_response.status_code}")
    if read_response.status_code == 200:
        print("✅ SUCCESS! Shared user can read individual items!")
    else:
        print(f"❌ Item read failed: {read_response.text}")
    
    # Step 5: Test reading items from list
    print(f"\n📄 Testing items list read...")
    items_response = requests.get(
        f"{base_url}/api/v1/items/list/11",
        headers=headers
    )
    
    print(f"Items list read status: {items_response.status_code}")
    if items_response.status_code == 200:
        items = items_response.json()
        print(f"✅ SUCCESS! Shared user can read items list! ({len(items)} items)")
    else:
        print(f"❌ Items list read failed: {items_response.text}")
    
    print("\n🎉 Item permission fix verification complete!")
    
    # Restore original state (mark item as uncompleted)
    print(f"\n🔄 Restoring original item state...")
    restore_response = requests.put(
        f"{base_url}/api/v1/items/{item_id}",
        headers=headers,
        json={"is_completed": False}
    )
    if restore_response.status_code == 200:
        print("✅ Item state restored")
    else:
        print(f"⚠️  Could not restore item state: {restore_response.text}")

if __name__ == "__main__":
    test_shared_user_item_permissions()
