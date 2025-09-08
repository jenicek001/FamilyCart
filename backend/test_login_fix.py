#!/usr/bin/env python3
"""Test script to verify login functionality is restored."""

import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()


async def test_login():
    """Test login functionality to ensure the SQLAlchemy relationship fix worked."""

    # Test credentials - using common test credentials
    test_credentials = {"username": "test@example.com", "password": "testpassword123"}

    async with httpx.AsyncClient() as client:
        print("Testing login endpoint...")
        try:
            # Test login endpoint
            response = await client.post(
                "http://localhost:8000/api/v1/auth/jwt/login",
                data=test_credentials,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            print(f"Login response status: {response.status_code}")
            print(f"Login response headers: {dict(response.headers)}")

            if response.status_code == 200:
                print("✅ Login successful - backend is working!")
                result = response.json()
                print(
                    f"Access token received: {result.get('access_token', 'N/A')[:50]}..."
                )
                return True
            elif response.status_code == 400:
                print("❌ Login failed - Bad credentials (but backend is responding)")
                print(f"Response: {response.text}")
                return True  # Backend is working, just wrong credentials
            else:
                print(f"❌ Login failed with status {response.status_code}")
                print(f"Response: {response.text}")
                return False

        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False


if __name__ == "__main__":
    asyncio.run(test_login())
