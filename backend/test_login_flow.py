#!/usr/bin/env python3
"""
Test login flow and check for WebSocket connection issues.
This simulates what happens when a user logs in through the frontend.
"""

import asyncio
import json
import sys

import httpx


async def test_login_flow():
    """Test the complete login flow that might trigger WebSocket issues"""

    base_url = "http://localhost:8000"

    async with httpx.AsyncClient() as client:
        print("🧪 Testing Login Flow & WebSocket Connection")
        print("=" * 50)

        # Test user credentials (Berta - the user mentioned in the issue)
        email = "berta.stepanova@gmail.com"
        password = "berta"

        # Step 1: Login to get token
        print(f"📋 Step 1: Logging in as {email}")
        login_data = {
            "username": email,  # FastAPI users typically use 'username' field
            "password": password,
        }

        try:
            login_response = await client.post(
                f"{base_url}/api/v1/auth/jwt/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            if login_response.status_code != 200:
                print(f"❌ Login failed with status {login_response.status_code}")
                print(f"Response: {login_response.text}")
                return False

            token_data = login_response.json()
            token = token_data.get("access_token")

            if not token:
                print(f"❌ No access token in response: {token_data}")
                return False

            print(f"✅ Login successful, token: {token[:20]}...")

        except Exception as e:
            print(f"❌ Login request failed: {e}")
            return False

        # Step 2: Fetch user info (like AuthContext.fetchUser() does)
        print(f"📋 Step 2: Fetching user info")
        headers = {"Authorization": f"Bearer {token}"}

        try:
            user_response = await client.get(
                f"{base_url}/api/v1/users/me", headers=headers
            )

            if user_response.status_code != 200:
                print(f"❌ User fetch failed with status {user_response.status_code}")
                return False

            user_data = user_response.json()
            print(
                f"✅ User data fetched: {user_data.get('email')} ({user_data.get('first_name')})"
            )

        except Exception as e:
            print(f"❌ User fetch failed: {e}")
            return False

        # Step 3: Fetch shopping lists (like dashboard would do)
        print(f"📋 Step 3: Fetching shopping lists")

        try:
            lists_response = await client.get(
                f"{base_url}/api/v1/shopping-lists", headers=headers
            )

            if lists_response.status_code != 200:
                print(f"❌ Lists fetch failed with status {lists_response.status_code}")
                return False

            lists_data = lists_response.json()
            print(f"✅ Found {len(lists_data)} shopping lists")

            if not lists_data:
                print("⚠️ No shopping lists found - cannot test WebSocket connection")
                return True

            # Use the first list for WebSocket testing
            list_id = lists_data[0]["id"]
            print(f"📋 Will test WebSocket connection to list {list_id}")

        except Exception as e:
            print(f"❌ Lists fetch failed: {e}")
            return False

        # Step 4: Test WebSocket connection (like RealtimeShoppingList would do)
        print(f"📋 Step 4: Testing WebSocket connection")

        try:
            import websockets

            ws_url = f"ws://localhost:8000/api/v1/ws/lists/{list_id}?token={token}"
            print(f"🔌 Connecting to: {ws_url}")

            async with websockets.connect(ws_url) as websocket:
                print("✅ WebSocket connection established!")

                # Send a ping
                await websocket.send(json.dumps({"type": "ping"}))
                print("📤 Sent ping")

                # Wait for response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    response_data = json.loads(response)
                    print(f"📥 Received: {response_data}")

                    # Keep connection open briefly
                    await asyncio.sleep(2)
                    print("✅ WebSocket test completed successfully")

                except asyncio.TimeoutError:
                    print("⏰ No WebSocket response within 5 seconds")

        except Exception as e:
            print(f"❌ WebSocket test failed: {e}")
            return False

        print("\n🎉 All login flow tests passed!")
        return True


async def main():
    """Main test function"""
    success = await test_login_flow()

    if success:
        print("\n✅ Login flow test completed successfully!")
        print("If WebSocket issues persist in frontend, the problem is likely in:")
        print("  - React component lifecycle management")
        print("  - Multiple rapid state changes during auth flow")
        print("  - Frontend error handling or toast notifications")
        sys.exit(0)
    else:
        print("\n❌ Login flow test failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
