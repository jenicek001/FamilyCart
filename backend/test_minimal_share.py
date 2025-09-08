#!/usr/bin/env python3
"""
Test Share Endpoint with Minimal Implementation
"""

import asyncio
import httpx


async def test_minimal_share():
    """Test share endpoint with minimal response to isolate the issue."""

    base_url = "http://localhost:8000"

    async with httpx.AsyncClient() as client:
        print("🔧 Testing Minimal Share Implementation")
        print("=" * 40)

        # Get existing token (assume users exist from previous tests)
        owner_login = {
            "username": "debug_owner@example.com",
            "password": "TestPassword123!",
        }
        response = await client.post(
            f"{base_url}/api/v1/auth/jwt/login",
            data=owner_login,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if response.status_code != 200:
            print("❌ Login failed")
            return

        owner_headers = {"Authorization": f"Bearer {response.json()['access_token']}"}

        # Create list
        response = await client.post(
            f"{base_url}/api/v1/shopping-lists",
            json={"name": "Minimal Test List"},
            headers=owner_headers,
        )

        if response.status_code != 200:
            print("❌ List creation failed")
            return

        list_id = response.json()["id"]
        print(f"✅ Created list {list_id}")

        # Test sharing with detailed error info
        share_data = {"email": "debug_member@example.com"}

        print(f"🔍 Attempting to share list {list_id}...")
        print(f"Share data: {share_data}")
        print(f"Headers: {owner_headers}")

        try:
            response = await client.post(
                f"{base_url}/api/v1/shopping-lists/{list_id}/share",
                json=share_data,
                headers=owner_headers,
                timeout=10.0,  # Add timeout
            )

            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            print(f"Response Text: {response.text}")

            if response.status_code == 200:
                data = response.json()
                print("✅ Share successful!")
                print(f"Shared list name: {data.get('name')}")
                if "members" in data:
                    print(f"Members count: {len(data['members'])}")
                else:
                    print("No members field in response")
            else:
                print(f"❌ Share failed with status {response.status_code}")

        except asyncio.TimeoutError:
            print("❌ Request timed out")
        except Exception as e:
            print(f"❌ Exception: {type(e).__name__}: {e}")


if __name__ == "__main__":
    asyncio.run(test_minimal_share())
