#!/usr/bin/env python3
"""
Create test users for frontend sharing testing
"""

import asyncio
import httpx


async def create_test_users():
    """Create test users for sharing functionality."""

    base_url = "http://localhost:8000"

    async with httpx.AsyncClient() as client:
        print("👥 Creating Test Users for Frontend Sharing")
        print("=" * 50)

        # Users to create
        users = [
            {
                "email": "debug_owner@example.com",
                "password": "TestPassword123!",
                "full_name": "Test Owner",
                "nickname": "Owner",
            },
            {
                "email": "debug_member@example.com",
                "password": "TestPassword123!",
                "full_name": "Test Member",
                "nickname": "Member",
            },
            {
                "email": "debug_member2@example.com",
                "password": "TestPassword123!",
                "full_name": "Test Member 2",
                "nickname": "Member2",
            },
        ]

        for user_data in users:
            try:
                response = await client.post(
                    f"{base_url}/api/v1/auth/register", json=user_data
                )

                if response.status_code == 201:
                    user = response.json()
                    print(f"✅ Created user: {user['email']} ({user['full_name']})")
                elif (
                    response.status_code == 400
                    and "already registered" in response.text.lower()
                ):
                    print(f"ℹ️  User already exists: {user_data['email']}")
                else:
                    print(
                        f"❌ Failed to create {user_data['email']}: {response.status_code} - {response.text}"
                    )

            except Exception as e:
                print(f"❌ Error creating {user_data['email']}: {e}")

        print("\n🎯 Frontend Testing Instructions:")
        print("1. Login as debug_owner@example.com")
        print("2. Create a shopping list")
        print("3. Click the share icon (right of list name)")
        print("4. Try inviting debug_member@example.com")
        print("5. Click the user icon to test the user menu")
        print("6. Check that both icons are now reactive to clicks!")


if __name__ == "__main__":
    asyncio.run(create_test_users())
