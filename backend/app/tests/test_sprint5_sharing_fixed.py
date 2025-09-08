import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from httpx import AsyncClient

from app.api.deps import get_shopping_list
from app.models.shopping_list import ShoppingList
from app.models.user import User
from app.models.item import Item
from app.schemas.share import ShareRequest
from app.services.notification_service import send_list_invitation_email


class TestSharingPermissions:
    """Test sharing and permission functionality for Sprint 5."""

    @pytest.mark.asyncio
    async def test_get_shopping_list_owner_access(self, test_db: AsyncSession):
        """Test that list owner can access their list via get_shopping_list dependency."""
        # Create test user and shopping list
        owner = User(
            email="owner@test.com",
            hashed_password="hashed",
            is_active=True,
            is_verified=True,
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
            email="owner@test.com",
            hashed_password="hashed",
            is_active=True,
            is_verified=True,
        )
        member = User(
            email="member@test.com",
            hashed_password="hashed",
            is_active=True,
            is_verified=True,
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
            email="owner@test.com",
            hashed_password="hashed",
            is_active=True,
            is_verified=True,
        )
        outsider = User(
            email="outsider@test.com",
            hashed_password="hashed",
            is_active=True,
            is_verified=True,
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
            email="user@test.com",
            hashed_password="hashed",
            is_active=True,
            is_verified=True,
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
        # Create owner and target user
        owner = User(
            email="owner@test.com",
            hashed_password="hashed",
            is_active=True,
            is_verified=True,
        )
        target_user = User(
            email="target@test.com",
            hashed_password="hashed",
            is_active=True,
            is_verified=True,
        )
        test_db.add_all([owner, target_user])
        await test_db.commit()
        await test_db.refresh(owner)
        await test_db.refresh(target_user)

        # Create shopping list
        shopping_list = ShoppingList(name="Test List", owner_id=owner.id)
        test_db.add(shopping_list)
        await test_db.commit()
        await test_db.refresh(shopping_list)

        # Mock authentication and websocket/email services
        with patch(
            "app.api.v1.endpoints.shopping_lists.current_user", return_value=owner
        ), patch(
            "app.api.v1.endpoints.shopping_lists.websocket_service.notify_list_shared",
            new_callable=AsyncMock,
        ), patch(
            "app.api.v1.endpoints.shopping_lists.send_list_invitation_email",
            new_callable=AsyncMock,
        ):

            response = await client.post(
                f"/api/v1/shopping_lists/{shopping_list.id}/share",
                json={"email": target_user.email},
            )

        assert response.status_code == 200

        # Verify user was added to shared_with
        await test_db.refresh(shopping_list)
        assert target_user in shopping_list.shared_with

    @pytest.mark.asyncio
    async def test_share_list_only_owner_can_share(
        self, test_db: AsyncSession, client: AsyncClient
    ):
        """Test that only list owners can share lists."""
        # Create owner, member, and target users
        owner = User(
            email="owner@test.com",
            hashed_password="hashed",
            is_active=True,
            is_verified=True,
        )
        member = User(
            email="member@test.com",
            hashed_password="hashed",
            is_active=True,
            is_verified=True,
        )
        target_user = User(
            email="target@test.com",
            hashed_password="hashed",
            is_active=True,
            is_verified=True,
        )
        test_db.add_all([owner, member, target_user])
        await test_db.commit()
        await test_db.refresh(owner)
        await test_db.refresh(member)

        # Create shopping list and share with member
        shopping_list = ShoppingList(name="Test List", owner_id=owner.id)
        shopping_list.shared_with.append(member)
        test_db.add(shopping_list)
        await test_db.commit()
        await test_db.refresh(shopping_list)

        # Mock authentication for member (not owner)
        with patch(
            "app.api.v1.endpoints.shopping_lists.current_user", return_value=member
        ):
            response = await client.post(
                f"/api/v1/shopping_lists/{shopping_list.id}/share",
                json={"email": target_user.email},
            )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_share_list_user_not_found(
        self, test_db: AsyncSession, client: AsyncClient
    ):
        """Test sharing with nonexistent user email."""
        # Create owner
        owner = User(
            email="owner@test.com",
            hashed_password="hashed",
            is_active=True,
            is_verified=True,
        )
        test_db.add(owner)
        await test_db.commit()
        await test_db.refresh(owner)

        # Create shopping list
        shopping_list = ShoppingList(name="Test List", owner_id=owner.id)
        test_db.add(shopping_list)
        await test_db.commit()
        await test_db.refresh(shopping_list)

        # Mock authentication
        with patch(
            "app.api.v1.endpoints.shopping_lists.current_user", return_value=owner
        ):
            response = await client.post(
                f"/api/v1/shopping_lists/{shopping_list.id}/share",
                json={"email": "nonexistent@test.com"},
            )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_share_list_already_shared(
        self, test_db: AsyncSession, client: AsyncClient
    ):
        """Test sharing with user who already has access."""
        # Create owner and target user
        owner = User(
            email="owner@test.com",
            hashed_password="hashed",
            is_active=True,
            is_verified=True,
        )
        target_user = User(
            email="target@test.com",
            hashed_password="hashed",
            is_active=True,
            is_verified=True,
        )
        test_db.add_all([owner, target_user])
        await test_db.commit()
        await test_db.refresh(owner)
        await test_db.refresh(target_user)

        # Create shopping list and share it
        shopping_list = ShoppingList(name="Test List", owner_id=owner.id)
        shopping_list.shared_with.append(target_user)
        test_db.add(shopping_list)
        await test_db.commit()
        await test_db.refresh(shopping_list)

        # Mock authentication
        with patch(
            "app.api.v1.endpoints.shopping_lists.current_user", return_value=owner
        ):
            response = await client.post(
                f"/api/v1/shopping_lists/{shopping_list.id}/share",
                json={"email": target_user.email},
            )

        # Should succeed but not duplicate the sharing
        assert response.status_code == 200


class TestItemPermissions:
    """Test item access permissions for shared lists."""

    @pytest.mark.asyncio
    async def test_shared_member_can_add_items(
        self, test_db: AsyncSession, client: AsyncClient
    ):
        """Test that shared members can add items to shared lists."""
        # Create owner and member
        owner = User(
            email="owner@test.com",
            hashed_password="hashed",
            is_active=True,
            is_verified=True,
        )
        member = User(
            email="member@test.com",
            hashed_password="hashed",
            is_active=True,
            is_verified=True,
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

        # Mock authentication and AI services
        with patch(
            "app.api.v1.endpoints.shopping_lists.current_user", return_value=member
        ), patch(
            "app.api.v1.endpoints.shopping_lists.ai_service.suggest_category_async",
            new_callable=AsyncMock,
            return_value="Groceries",
        ), patch(
            "app.api.v1.endpoints.shopping_lists.ai_service.standardize_and_translate_item_name",
            new_callable=AsyncMock,
            return_value={"standardized_name": "Milk", "translations": {}},
        ), patch(
            "app.api.v1.endpoints.shopping_lists.ai_service.suggest_icon",
            new_callable=AsyncMock,
            return_value="milk",
        ), patch(
            "app.api.v1.endpoints.shopping_lists.websocket_service.notify_item_created",
            new_callable=AsyncMock,
        ):

            response = await client.post(
                f"/api/v1/shopping_lists/{shopping_list.id}/items",
                json={"name": "Milk", "quantity": "1L"},
            )

        assert response.status_code == 200

        # Verify item was created
        result = await test_db.execute(
            select(Item).where(Item.shopping_list_id == shopping_list.id)
        )
        items = result.scalars().all()
        assert len(items) == 1
        assert items[0].name == "Milk"
        assert items[0].owner_id == member.id

    @pytest.mark.asyncio
    async def test_shared_member_can_read_items(
        self, test_db: AsyncSession, client: AsyncClient
    ):
        """Test that shared members can read items from shared lists."""
        # Create owner, member, and item
        owner = User(
            email="owner@test.com",
            hashed_password="hashed",
            is_active=True,
            is_verified=True,
        )
        member = User(
            email="member@test.com",
            hashed_password="hashed",
            is_active=True,
            is_verified=True,
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

        # Create item
        item = Item(
            name="Test Item",
            shopping_list_id=shopping_list.id,
            owner_id=owner.id,
            last_modified_by_id=owner.id,
        )
        test_db.add(item)
        await test_db.commit()

        # Mock authentication
        with patch(
            "app.api.v1.endpoints.shopping_lists.current_user", return_value=member
        ):
            response = await client.get(
                f"/api/v1/shopping_lists/{shopping_list.id}/items"
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Test Item"


class TestNotificationService:
    """Test notification service functionality."""

    def test_send_list_invitation_email(self):
        """Test email invitation sending (mocked)."""
        # This test verifies the function exists and can be called
        # In a real implementation, this would test email sending logic
        from app.services.notification_service import send_list_invitation_email

        # Mock the email sending
        with patch(
            "app.services.notification_service.send_list_invitation_email"
        ) as mock_send:
            mock_send.return_value = None

            # Call the function with correct parameters
            send_list_invitation_email(
                to_email="test@example.com",
                list_data={"name": "Test List"},
                inviter_email="owner@example.com",
            )

            # Verify it was called
            mock_send.assert_called_once_with(
                to_email="test@example.com",
                list_data={"name": "Test List"},
                inviter_email="owner@example.com",
            )
