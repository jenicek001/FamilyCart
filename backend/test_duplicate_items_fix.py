#!/usr/bin/env python3
"""
Test script to verify the fix for duplicate items in the frontend.

This script:
1. Creates a test item via the API
2. Monitors WebSocket events
3. Checks that only one item is created (not duplicated)
"""

import asyncio
import json
import websockets
import requests
import os
from typing import Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8000"
WS_BASE_URL = "ws://localhost:8000"

# Test user credentials (adjust as needed)
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpass123"

async def test_duplicate_items_fix():
    """Test that adding items doesn't create duplicates via WebSocket."""
    
    print("🧪 Testing duplicate items fix...")
    
    # Step 1: Login and get token
    print("📝 Logging in...")
    login_response = requests.post(f"{API_BASE_URL}/api/v1/auth/login", data={
        "username": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return False
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful")
    
    # Step 2: Get or create a shopping list
    print("📋 Getting shopping lists...")
    lists_response = requests.get(f"{API_BASE_URL}/api/v1/shopping-lists/", headers=headers)
    
    if lists_response.status_code != 200:
        print(f"❌ Failed to get lists: {lists_response.text}")
        return False
    
    lists = lists_response.json()
    
    if not lists:
        print("📝 Creating a test shopping list...")
        create_response = requests.post(
            f"{API_BASE_URL}/api/v1/shopping-lists/",
            headers=headers,
            json={"name": "Test List for Duplicate Fix"}
        )
        if create_response.status_code != 200:
            print(f"❌ Failed to create list: {create_response.text}")
            return False
        test_list = create_response.json()
    else:
        test_list = lists[0]
    
    list_id = test_list["id"]
    print(f"✅ Using list: {test_list['name']} (ID: {list_id})")
    
    # Step 3: Connect to WebSocket and monitor events
    ws_url = f"{WS_BASE_URL}/api/v1/ws/lists/{list_id}?token={token}"
    print(f"🔗 Connecting to WebSocket: {ws_url}")
    
    item_creation_events = []
    
    try:
        async with websockets.connect(ws_url) as websocket:
            print("✅ WebSocket connected")
            
            # Create a task to listen for WebSocket messages
            async def listen_for_messages():
                while True:
                    try:
                        message = await websocket.recv()
                        data = json.loads(message)
                        print(f"📨 WebSocket message: {data}")
                        
                        if data.get("type") == "item_change" and data.get("event_type") == "created":
                            item_creation_events.append(data)
                            print(f"🆕 Item creation event received: {data.get('item', {}).get('name')}")
                            
                    except websockets.exceptions.ConnectionClosed:
                        print("🔌 WebSocket connection closed")
                        break
                    except Exception as e:
                        print(f"❌ Error listening to WebSocket: {e}")
                        break
            
            # Start listening task
            listen_task = asyncio.create_task(listen_for_messages())
            
            # Wait a moment to ensure connection is stable
            await asyncio.sleep(1)
            
            # Step 4: Add a test item via API
            test_item_name = f"Test Item {asyncio.get_event_loop().time()}"
            print(f"🛒 Adding test item: {test_item_name}")
            
            add_item_response = requests.post(
                f"{API_BASE_URL}/api/v1/shopping-lists/{list_id}/items/",
                headers=headers,
                json={
                    "name": test_item_name,
                    "quantity": "1",
                    "description": "Test item for duplicate fix",
                    "category_name": "Test Category"
                }
            )
            
            if add_item_response.status_code != 200:
                print(f"❌ Failed to add item: {add_item_response.text}")
                return False
            
            created_item = add_item_response.json()
            print(f"✅ Item created via API: {created_item['name']} (ID: {created_item['id']})")
            
            # Step 5: Wait for WebSocket events
            print("⏳ Waiting for WebSocket events (5 seconds)...")
            await asyncio.sleep(5)
            
            # Cancel the listening task
            listen_task.cancel()
            
            # Step 6: Analyze results
            print(f"\n📊 Analysis:")
            print(f"   • Item creation events received: {len(item_creation_events)}")
            
            if len(item_creation_events) == 0:
                print("❌ No WebSocket events received - this might indicate an issue")
                return False
            elif len(item_creation_events) == 1:
                event = item_creation_events[0]
                event_item = event.get("item", {})
                if event_item.get("name") == test_item_name:
                    print("✅ Exactly one item creation event received - no duplicates!")
                    print(f"   • Event item: {event_item.get('name')} (ID: {event_item.get('id')})")
                    return True
                else:
                    print(f"❌ Event for different item: {event_item.get('name')}")
                    return False
            else:
                print(f"❌ Multiple item creation events received - duplicates detected!")
                for i, event in enumerate(item_creation_events):
                    event_item = event.get("item", {})
                    print(f"   • Event {i+1}: {event_item.get('name')} (ID: {event_item.get('id')})")
                return False
                
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")
        return False

async def main():
    """Main test function."""
    print("🚀 Starting duplicate items fix test\n")
    
    success = await test_duplicate_items_fix()
    
    print(f"\n{'='*50}")
    if success:
        print("✅ TEST PASSED: No duplicate items detected!")
        print("   The frontend fix is working correctly.")
    else:
        print("❌ TEST FAILED: Duplicate items or other issues detected!")
        print("   The frontend might still have the duplicate items bug.")
    print(f"{'='*50}")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)
