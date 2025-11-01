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


class TestItemPermissions:
    """Test item access permissions for shared lists."""

    @pytest.mark.asyncio
    async def test_shared_member_can_add_items(
        self, test_db: AsyncSession, client: AsyncClient
    ):
        """Test that shared members can add items to shared lists."""
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
            json={"name": "Shared List", "description": "Test"},
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

        # Add item as member
        response = await client.post(
            f"/api/v1/shopping-lists/{shopping_list_id}/items",
            json={"name": "Milk", "quantity": "1L"},
            headers=member_headers,
        )

        assert response.status_code == 200
        item_data = response.json()
        assert item_data["name"] == "Milk"

    @pytest.mark.asyncio
    async def test_shared_member_can_read_items(
        self, test_db: AsyncSession, client: AsyncClient
    ):
        """Test that shared members can read items from shared lists."""
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
            json={"name": "Shared List", "description": "Test"},
            headers=owner_headers,
        )
        shopping_list_id = list_response.json()["id"]

        # Add item as owner
        item_response = await client.post(
            f"/api/v1/shopping-lists/{shopping_list_id}/items",
            json={"name": "Test Item", "quantity": "1"},
            headers=owner_headers,
        )

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

        # Read items as member
        response = await client.get(
            f"/api/v1/shopping-lists/{shopping_list_id}/items",
            headers=member_headers,
        )

        assert response.status_code == 200
        items = response.json()
        assert len(items) >= 1
        assert any(item["name"] == "Test Item" for item in items)


