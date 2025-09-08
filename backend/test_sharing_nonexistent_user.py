#!/usr/bin/env python3
"""
Test script to verify sharing behavior with non-existent user email.
"""
import asyncio
import json
import httpx


async def test_sharing_nonexistent_user():
    base_url = "http://localhost:8000"

    # Login as the owner
    owner_login_data = {
        "username": "debug_owner@example.com",
        "password": "password123",
    }

    async with httpx.AsyncClient() as client:
        # Login
        print("🔐 Logging in as owner...")
        login_response = await client.post(
            f"{base_url}/api/v1/auth/jwt/login", data=owner_login_data
        )

        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(login_response.text)
            return

        # Get token
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get the owner's shopping lists
        print("📋 Getting shopping lists...")
        lists_response = await client.get(
            f"{base_url}/api/v1/shopping-lists/", headers=headers
        )

        if lists_response.status_code != 200:
            print(f"❌ Failed to get lists: {lists_response.status_code}")
            return

        lists = lists_response.json()
        if not lists:
            print("❌ No shopping lists found")
            return

        list_id = lists[0]["id"]
        list_name = lists[0]["name"]
        print(f"📝 Using list: {list_name} (ID: {list_id})")

        # Try to share with non-existent user
        print("📤 Trying to share with non-existent user...")
        share_data = {"email": "nonexistent_user@example.com"}

        share_response = await client.post(
            f"{base_url}/api/v1/shopping-lists/{list_id}/share",
            headers=headers,
            json=share_data,
        )

        print(f"📋 Share response status: {share_response.status_code}")
        print(f"📋 Share response: {share_response.text}")

        if share_response.status_code == 404:
            print("✅ Correctly returned 404 for non-existent user")
        else:
            print(f"⚠️  Unexpected status code: {share_response.status_code}")


if __name__ == "__main__":
    asyncio.run(test_sharing_nonexistent_user())
