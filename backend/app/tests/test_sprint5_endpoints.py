import asyncio
import uuid
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_shopping_list
from app.models.item import Item
from app.models.shopping_list import ShoppingList
from app.models.user import User
from app.schemas.share import ShareRequest
from app.services.notification_service import send_list_invitation_email


class TestSharingEndpoints:
    """Test sharing endpoint functionality."""

    @pytest.mark.asyncio
    async def test_share_list_success(self, test_db: AsyncSession, client: AsyncClient):
        """Test successful list sharing."""
        # Create owner via registration
        owner_email = f"owner-{uuid.uuid4().hex[:8]}@test.com"
        reg_response = await client.post(
            "/api/v1/auth/register",
            json={"email": owner_email, "password": "testpass123", "nickname": "Owner"},
        )
        assert reg_response.status_code in [
            200,
            201,
        ], f"Owner registration failed: {reg_response.status_code} - {reg_response.text}"

        # Create target user via registration
        target_email = f"target-{uuid.uuid4().hex[:8]}@test.com"
        reg_response2 = await client.post(
            "/api/v1/auth/register",
            json={
                "email": target_email,
                "password": "testpass123",
                "nickname": "Target",
            },
        )
        assert reg_response2.status_code in [
            200,
            201,
        ], f"Target registration failed: {reg_response2.status_code} - {reg_response2.text}"

        # Login as owner
        login_response = await client.post(
            "/api/v1/auth/jwt/login",
            data={"username": owner_email, "password": "testpass123"},
        )
        assert (
            login_response.status_code == 200
        ), f"Login failed: {login_response.status_code} - {login_response.text}"
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create shopping list as owner
        list_response = await client.post(
            "/api/v1/shopping-lists",
            json={"name": "Test List", "description": "Test"},
            headers=headers,
        )
        assert list_response.status_code in [
            200,
            201,
        ], f"List creation failed: {list_response.status_code} - {list_response.text}"
        shopping_list_id = list_response.json()["id"]

        # Share the list
        response = await client.post(
            f"/api/v1/shopping-lists/{shopping_list_id}/share",
            json={"email": target_email},
            headers=headers,
        )

        assert response.status_code == 200
        response_data = response.json()

        # Verify user was added to members
        assert any(user["email"] == target_email for user in response_data["members"])

    @pytest.mark.asyncio
    async def test_share_list_only_owner_can_share(
        self, test_db: AsyncSession, client: AsyncClient
    ):
        """Test that only list owners can share lists."""
        # Create owner via registration
        owner_email = f"owner-{uuid.uuid4().hex[:8]}@test.com"
        await client.post(
            "/api/v1/auth/register",
            json={"email": owner_email, "password": "testpass123", "nickname": "Owner"},
        )

        # Create member via registration
        member_email = f"member-{uuid.uuid4().hex[:8]}@test.com"
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": member_email,
                "password": "testpass123",
                "nickname": "Member",
            },
        )

        # Create target user via registration
        target_email = f"target-{uuid.uuid4().hex[:8]}@test.com"
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": target_email,
                "password": "testpass123",
                "nickname": "Target",
            },
        )

        # Login as owner
        owner_login = await client.post(
            "/api/v1/auth/jwt/login",
            data={"username": owner_email, "password": "testpass123"},
        )
        owner_token = owner_login.json()["access_token"]
        owner_headers = {"Authorization": f"Bearer {owner_token}"}

        # Create shopping list as owner
        list_response = await client.post(
            "/api/v1/shopping-lists",
            json={"name": "Test List", "description": "Test"},
            headers=owner_headers,
        )
        shopping_list_id = list_response.json()["id"]

        # Share the list with member
        await client.post(
            f"/api/v1/shopping-lists/{shopping_list_id}/share",
            json={"email": member_email},
            headers=owner_headers,
        )

        # Login as member
        member_login = await client.post(
            "/api/v1/auth/jwt/login",
            data={"username": member_email, "password": "testpass123"},
        )
        member_token = member_login.json()["access_token"]
        member_headers = {"Authorization": f"Bearer {member_token}"}

        # Try to share as member (should fail)
        response = await client.post(
            f"/api/v1/shopping-lists/{shopping_list_id}/share",
            json={"email": target_email},
            headers=member_headers,
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_share_list_user_not_found(
        self, test_db: AsyncSession, client: AsyncClient
    ):
        """Test sharing with nonexistent user email sends invitation."""
        # Create owner via registration
        owner_email = f"owner-{uuid.uuid4().hex[:8]}@test.com"
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": owner_email,
                "password": "Password123!",
                "nickname": "TestOwner",
            },
        )

        # Login as owner
        login_response = await client.post(
            "/api/v1/auth/jwt/login",
            data={"username": owner_email, "password": "Password123!"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create shopping list
        list_response = await client.post(
            "/api/v1/shopping-lists",
            json={"name": "Test List", "description": "Test"},
            headers=headers,
        )
        shopping_list_id = list_response.json()["id"]

        # Share with nonexistent user should send invitation and return 200
        response = await client.post(
            f"/api/v1/shopping-lists/{shopping_list_id}/share",
            json={"email": "nonexistent@test.com"},
            headers=headers,
        )

        # Should succeed and send invitation email
        assert response.status_code == 200
        # User should not be in members list since they don't exist yet
        response_data = response.json()
        assert len(response_data["members"]) == 0

    @pytest.mark.asyncio
    async def test_share_list_already_shared(
        self, test_db: AsyncSession, client: AsyncClient
    ):
        """Test sharing with user who already has access."""
        # Create owner via registration
        owner_email = f"owner-{uuid.uuid4().hex[:8]}@test.com"
        await client.post(
            "/api/v1/auth/register",
            json={"email": owner_email, "password": "testpass123", "nickname": "Owner"},
        )

        # Create target user via registration
        target_email = f"target-{uuid.uuid4().hex[:8]}@test.com"
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": target_email,
                "password": "testpass123",
                "nickname": "Target",
            },
        )

        # Login as owner
        login_response = await client.post(
            "/api/v1/auth/jwt/login",
            data={"username": owner_email, "password": "testpass123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create shopping list as owner
        list_response = await client.post(
            "/api/v1/shopping-lists",
            json={"name": "Test List", "description": "Test"},
            headers=headers,
        )
        shopping_list_id = list_response.json()["id"]

        # Share the list first time
        await client.post(
            f"/api/v1/shopping-lists/{shopping_list_id}/share",
            json={"email": target_email},
            headers=headers,
        )

        # Share again (should succeed but not duplicate)
        response = await client.post(
            f"/api/v1/shopping-lists/{shopping_list_id}/share",
            json={"email": target_email},
            headers=headers,
        )

        # Should succeed but not duplicate the sharing
        assert response.status_code == 200
        response_data = response.json()

        # Verify user appears only once in members
        shared_emails = [user["email"] for user in response_data["members"]]
        assert shared_emails.count(target_email) == 1


