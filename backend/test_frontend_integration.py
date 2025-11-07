#!/usr/bin/env python3
"""
Test Frontend Sharing UI Integration
"""

import asyncio

import httpx


async def test_frontend_sharing_integration():
    """Test sharing functionality for frontend integration."""

    base_url = "http://localhost:8000"

    async with httpx.AsyncClient() as client:
        print("🧪 Testing Frontend Sharing UI Integration")
        print("=" * 50)

        # Login as owner
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
            print("❌ Owner login failed")
            return

        owner_headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
        print("✅ Owner logged in")

        # Create a test list
        response = await client.post(
            f"{base_url}/api/v1/shopping-lists",
            json={"name": "Frontend Test List"},
            headers=owner_headers,
        )

        if response.status_code != 200:
            print("❌ List creation failed")
            return

        list_data = response.json()
        list_id = list_data["id"]
        print(f"✅ Created list: {list_data['name']} (ID: {list_id})")

        # Test sharing (invite member)
        share_data = {"email": "debug_member@example.com"}
        response = await client.post(
            f"{base_url}/api/v1/shopping-lists/{list_id}/share",
            json=share_data,
            headers=owner_headers,
        )

        if response.status_code == 200:
            shared_list = response.json()
            print(
                f"✅ Share successful! List has {len(shared_list.get('members', []))} members"
            )

            # Verify the returned structure matches frontend expectations
            required_fields = ["id", "name", "owner_id", "members", "items"]
            missing_fields = [
                field for field in required_fields if field not in shared_list
            ]

            if missing_fields:
                print(f"⚠️  Missing fields in response: {missing_fields}")
            else:
                print("✅ Response structure matches frontend expectations")

            # Check member structure
            if shared_list.get("members"):
                member = shared_list["members"][0]
                member_fields = ["id", "email", "full_name"]
                missing_member_fields = [
                    field for field in member_fields if field not in member
                ]

                if missing_member_fields:
                    print(f"⚠️  Missing member fields: {missing_member_fields}")
                else:
                    print("✅ Member structure is correct")
        else:
            print(f"❌ Share failed: {response.status_code} - {response.text}")

        # Test user profile endpoint (for UserBadge)
        response = await client.get(
            f"{base_url}/api/v1/users/me", headers=owner_headers
        )

        if response.status_code == 200:
            user_data = response.json()
            user_fields = ["id", "email", "full_name"]
            missing_user_fields = [
                field for field in user_fields if field not in user_data
            ]

            if missing_user_fields:
                print(f"⚠️  Missing user fields: {missing_user_fields}")
            else:
                print("✅ User profile structure is correct")
        else:
            print(f"❌ User profile fetch failed: {response.status_code}")

        print("\n🎯 Frontend Integration Test Summary:")
        print("- Share button should open ShareDialog")
        print("- User menu should show UserMenu with logout option")
        print("- Both components should be functional and responsive")
        print("- Share dialog should handle email invitations")
        print("- User menu should display current user info")


if __name__ == "__main__":
    asyncio.run(test_frontend_sharing_integration())
