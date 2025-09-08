import pytest
import asyncio
from httpx import AsyncClient
import uuid
import os
import sys

# Add the parent directory to sys.path to allow importing from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_auth_flow():
    """
    Test the complete authentication flow:
    1. Register a new user
    2. Login with the user credentials
    3. Access a protected endpoint (shopping lists)
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Generate random email to avoid conflicts
        test_email = f"test_{uuid.uuid4()}@example.com"
        test_password = "StrongPassword123!"

        # Step 1: Register a new user
        register_data = {
            "email": test_email,
            "password": test_password,
            "first_name": "Test",
            "last_name": "User",
            "nickname": "TestUser",
        }

        register_response = await client.post(
            "/api/v1/auth/register", json=register_data
        )
        print(f"Register response status: {register_response.status_code}")
        print(f"Register response body: {register_response.json()}")

        assert register_response.status_code == 201

        # Step 2: Login with the new user
        login_data = {
            "username": test_email,
            "password": test_password,
        }

        login_response = await client.post(
            "/api/v1/auth/jwt/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        print(f"Login response status: {login_response.status_code}")
        print(f"Login response body: {login_response.json()}")

        assert login_response.status_code == 200
        token_data = login_response.json()
        assert "access_token" in token_data
        access_token = token_data["access_token"]

        # Step 3: Access a protected endpoint (shopping lists)
        lists_response = await client.get(
            "/api/v1/shopping-lists",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        print(f"Lists response status: {lists_response.status_code}")

        # Should return 200 OK with an empty list (new user has no lists yet)
        assert lists_response.status_code == 200
        lists_data = lists_response.json()
        assert isinstance(lists_data, list)

        # Try without auth token (should fail)
        lists_no_auth_response = await client.get("/api/v1/shopping-lists")
        assert lists_no_auth_response.status_code == 401


# Run the test directly if this file is executed
if __name__ == "__main__":
    asyncio.run(test_auth_flow())
