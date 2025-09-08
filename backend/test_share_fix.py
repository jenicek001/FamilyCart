#!/usr/bin/env python3
"""
Test script to verify the share endpoint serialization fix.
"""
import asyncio
import aiohttp
import json


async def test_share_endpoint():
    async with aiohttp.ClientSession() as session:
        # Step 1: Login as a user who owns a shopping list
        login_data = {
            "username": "debug_owner@example.com",
            "password": "TestPassword123!",
        }

        async with session.post(
            "http://localhost:8000/api/v1/auth/jwt/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        ) as resp:
            if resp.status != 200:
                print(f"Login failed: {resp.status}")
                text = await resp.text()
                print(f"Response: {text}")
                return

            login_result = await resp.json()
            token = login_result["access_token"]
            print(f"Login successful, token: {token[:50]}...")

        # Step 2: Get owned shopping lists to find a valid list ID
        async with session.get(
            "http://localhost:8000/api/v1/shopping-lists/",
            headers={"Authorization": f"Bearer {token}"},
        ) as resp:
            if resp.status != 200:
                print(f"Failed to get shopping lists: {resp.status}")
                text = await resp.text()
                print(f"Response: {text}")
                return

            lists = await resp.json()
            if not lists:
                print("No shopping lists found")
                return

            list_id = lists[0]["id"]
            print(f"Using shopping list ID: {list_id}")

        # Step 3: Test sharing with an existing user
        share_data = {"email": "debug_member@example.com"}  # This user exists in our DB

        async with session.post(
            f"http://localhost:8000/api/v1/shopping-lists/{list_id}/share",
            json=share_data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        ) as resp:
            print(f"Share endpoint status: {resp.status}")
            text = await resp.text()

            if resp.status == 200:
                print("✅ Share endpoint successful! Serialization issue fixed.")
                result = json.loads(text)
                print(
                    f"Response contains {len(result.get('items', []))} items and {len(result.get('members', []))} members"
                )
            else:
                print(f"❌ Share endpoint failed: {resp.status}")
                print(f"Response: {text}")

        # Step 4: Test sharing with a non-existent user
        share_data_nonexistent = {"email": "nonexistent@example.com"}

        async with session.post(
            f"http://localhost:8000/api/v1/shopping-lists/{list_id}/share",
            json=share_data_nonexistent,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        ) as resp:
            print(f"\nNon-existent user share status: {resp.status}")
            text = await resp.text()

            if resp.status == 200:
                print("✅ Non-existent user share successful!")
                result = json.loads(text)
                print(
                    f"Response contains {len(result.get('items', []))} items and {len(result.get('members', []))} members"
                )
            else:
                print(f"❌ Non-existent user share failed: {resp.status}")
                print(f"Response: {text}")


if __name__ == "__main__":
    asyncio.run(test_share_endpoint())
