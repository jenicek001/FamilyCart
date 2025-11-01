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


class TestSharingPermissions:
    """Test sharing and permission functionality for Sprint 5."""

    @pytest.mark.asyncio
    async def test_get_shopping_list_owner_access(self, test_db: AsyncSession):
        """Test that list owner can access their list via get_shopping_list dependency."""
        # Create test user and shopping list
        owner = User(
            email=f"owner-{uuid.uuid4().hex[:8]}@test.com",
            hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYctHWLSbaC",
            is_active=True,
            is_verified=True,
            nickname="TestUser",
        )
        test_db.add(owner)
        await test_db.commit()
        await test_db.refresh(owner)

        shopping_list = ShoppingList(name="Test List", owner_id=owner.id)
        test_db.add(shopping_list)
        await test_db.commit()
        await test_db.refresh(shopping_list)

        # Test get_shopping_list allows owner access
        result = await get_shopping_list(
            list_id=shopping_list.id, session=test_db, current_user=owner
        )

        assert result.id == shopping_list.id
        assert result.owner_id == owner.id

    @pytest.mark.asyncio
    async def test_get_shopping_list_shared_member_access(self, test_db: AsyncSession):
        """Test that shared members can access shared lists."""
        # Create owner and member users
        owner = User(
            email=f"owner-{uuid.uuid4().hex[:8]}@test.com",
            hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYctHWLSbaC",
            is_active=True,
            is_verified=True,
            nickname="TestUser",
        )
        member = User(
            email=f"member-{uuid.uuid4().hex[:8]}@test.com",
            hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYctHWLSbaC",
            is_active=True,
            is_verified=True,
            nickname="TestUser",
        )
        test_db.add_all([owner, member])
        await test_db.commit()
        await test_db.refresh(owner)
        await test_db.refresh(member)

        # Create shopping list and share it
        shopping_list = ShoppingList(name="Shared List", owner_id=owner.id)
        shopping_list.shared_with.append(member)
        test_db.add(shopping_list)
        await test_db.commit()
        await test_db.refresh(shopping_list)

        # Test get_shopping_list allows shared member access
        result = await get_shopping_list(
            list_id=shopping_list.id, session=test_db, current_user=member
        )

        assert result.id == shopping_list.id
        assert result.owner_id == owner.id

    @pytest.mark.asyncio
    async def test_get_shopping_list_unauthorized_access(self, test_db: AsyncSession):
        """Test that unauthorized users cannot access lists."""
        from fastapi import HTTPException

        # Create users
        owner = User(
            email=f"owner-{uuid.uuid4().hex[:8]}@test.com",
            hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYctHWLSbaC",
            is_active=True,
            is_verified=True,
            nickname="TestUser",
        )
        outsider = User(
            email=f"outsider-{uuid.uuid4().hex[:8]}@test.com",
            hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYctHWLSbaC",
            is_active=True,
            is_verified=True,
            nickname="TestUser",
        )
        test_db.add_all([owner, outsider])
        await test_db.commit()
        await test_db.refresh(owner)
        await test_db.refresh(outsider)

        # Create shopping list
        shopping_list = ShoppingList(name="Private List", owner_id=owner.id)
        test_db.add(shopping_list)
        await test_db.commit()
        await test_db.refresh(shopping_list)

        # Test get_shopping_list denies unauthorized access
        with pytest.raises(HTTPException) as exc_info:
            await get_shopping_list(
                list_id=shopping_list.id, session=test_db, current_user=outsider
            )

        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_get_shopping_list_nonexistent(self, test_db: AsyncSession):
        """Test that accessing nonexistent list raises 404."""
        from fastapi import HTTPException

        user = User(
            email=f"user-{uuid.uuid4().hex[:8]}@test.com",
            hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYctHWLSbaC",
            is_active=True,
            is_verified=True,
            nickname="TestUser",
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        # Test get_shopping_list raises 404 for nonexistent list
        with pytest.raises(HTTPException) as exc_info:
            await get_shopping_list(list_id=99999, session=test_db, current_user=user)

        assert exc_info.value.status_code == 404


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


class TestNotificationService:
    """Test notification service functionality."""

    async def test_send_list_invitation_email(self):
        """Test email invitation sending (mocked)."""
        # This test verifies the function exists and can be called
        from app.services.notification_service import send_list_invitation_email

        # Mock print to verify the function executes without errors
        with patch("builtins.print") as mock_print:
            await send_list_invitation_email(
                to_email="test@example.com",
                list_data={"name": "Test List"},
                inviter_email="owner@example.com",
            )

            # Verify it was called (print was executed)
            mock_print.assert_called_once()
