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


