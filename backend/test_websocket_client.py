#!/usr/bin/env python3
"""
Simple WebSocket test client to verify real-time functionality.
This script connects to the WebSocket endpoint and tests basic functionality.
"""

import asyncio
import json
import sys
from datetime import datetime

import requests
import websockets

# Configuration
BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"


async def test_websocket_connection():
    """Test WebSocket connection and basic functionality"""

    print("🚀 Starting WebSocket Real-time Test")
    print("=" * 50)

    # Step 1: Register/Login to get JWT token
    print("📝 Step 1: Authentication...")

    # Try to register (might fail if user exists)
    register_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "name": "Test User",
    }

    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=register_data)
        if response.status_code in [200, 201]:
            print("✅ User registered successfully")
        elif response.status_code == 400:
            print("ℹ️  User already exists, proceeding to login")
        else:
            print(f"❌ Registration failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Registration error: {e}")

    # Login to get token
    login_data = {
        "username": TEST_EMAIL,  # FastAPI users typically uses 'username' field
        "password": TEST_PASSWORD,
    }

    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", data=login_data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            print("✅ Login successful")
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return

    # Step 2: Create a test shopping list
    print("\n📋 Step 2: Creating test shopping list...")

    headers = {"Authorization": f"Bearer {access_token}"}
    list_data = {
        "name": f"WebSocket Test List {datetime.now().strftime('%H:%M:%S')}",
        "description": "Test list for WebSocket functionality",
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/shopping-lists/", json=list_data, headers=headers
        )
        if response.status_code in [200, 201]:
            shopping_list = response.json()
            list_id = shopping_list["id"]
            print(f"✅ Shopping list created with ID: {list_id}")
        else:
            print(
                f"❌ Failed to create shopping list: {response.status_code} - {response.text}"
            )
            return
    except Exception as e:
        print(f"❌ Shopping list creation error: {e}")
        return

    # Step 3: Connect to WebSocket
    print(f"\n🔌 Step 3: Connecting to WebSocket (List ID: {list_id})...")

    ws_url = f"{WS_URL}/api/v1/ws/lists/{list_id}?token={access_token}"

    try:
        async with websockets.connect(ws_url) as websocket:
            print("✅ WebSocket connected successfully!")

            # Step 4: Test ping/pong
            print("\n🏓 Step 4: Testing ping/pong...")

            ping_message = {"type": "ping"}
            await websocket.send(json.dumps(ping_message))

            # Wait for pong response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                pong_data = json.loads(response)
                if pong_data.get("type") == "pong":
                    print("✅ Ping/pong successful")
                else:
                    print(f"⚠️  Unexpected response: {pong_data}")
            except asyncio.TimeoutError:
                print("❌ Ping/pong timeout")

            # Step 5: Create an item and listen for real-time updates
            print(f"\n📦 Step 5: Testing real-time item creation...")

            # Start listening for WebSocket messages
            listen_task = asyncio.create_task(listen_for_messages(websocket))

            # Wait a moment to ensure WebSocket is ready
            await asyncio.sleep(1)

            # Create an item via API
            item_data = {
                "name": "WebSocket Test Item",
                "quantity": 1,
                "description": "Test item for real-time updates",
            }

            try:
                response = requests.post(
                    f"{BASE_URL}/api/v1/shopping-lists/{list_id}/items",
                    json=item_data,
                    headers=headers,
                )
                if response.status_code in [200, 201]:
                    item = response.json()
                    print(f"✅ Item created via API: {item['name']}")
                else:
                    print(
                        f"❌ Failed to create item: {response.status_code} - {response.text}"
                    )
            except Exception as e:
                print(f"❌ Item creation error: {e}")

            # Wait for WebSocket message
            await asyncio.sleep(3)

            # Cancel the listening task
            listen_task.cancel()

            print("\n🎉 WebSocket test completed!")

    except websockets.exceptions.ConnectionClosed as e:
        print(f"❌ WebSocket connection closed: {e}")
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ WebSocket connection failed with status {e.status_code}")
        if e.status_code == 1008:
            print("   This usually means authentication failed")
        elif e.status_code == 1003:
            print("   This usually means you don't have access to this list")
    except Exception as e:
        print(f"❌ WebSocket error: {e}")


async def listen_for_messages(websocket):
    """Listen for incoming WebSocket messages"""
    try:
        while True:
            message = await websocket.recv()
            data = json.loads(message)

            print(f"\n📨 Received WebSocket message:")
            print(f"   Type: {data.get('type')}")
            print(f"   Event: {data.get('event_type', 'N/A')}")

            if data.get("type") == "item_change":
                item = data.get("item", {})
                print(f"   Item: {item.get('name', 'Unknown')}")
                print(f"   List ID: {data.get('list_id')}")
                print("✅ Real-time item update received!")
            elif data.get("type") == "list_change":
                print(f"   List ID: {data.get('list_id')}")
                print("✅ Real-time list update received!")
            elif data.get("type") == "pong":
                print(f"   Timestamp: {data.get('timestamp')}")

    except websockets.exceptions.ConnectionClosed:
        print("🔌 WebSocket connection closed")
    except asyncio.CancelledError:
        print("🔌 WebSocket listening cancelled")
    except Exception as e:
        print(f"❌ Error listening to WebSocket: {e}")


if __name__ == "__main__":
    print("FamilyCart WebSocket Test Client")
    print("Make sure the backend is running on localhost:8000")
    print()

    try:
        asyncio.run(test_websocket_connection())
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
