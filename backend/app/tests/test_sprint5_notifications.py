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
