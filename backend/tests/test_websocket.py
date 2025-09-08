"""
Tests for WebSocket real-time notifications functionality.
"""

import pytest
import asyncio
import json
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket
from unittest.mock import Mock, AsyncMock, patch
import jwt

from app.services.websocket_service import websocket_service
from app.api.v1.ws.notifications import ListConnectionManager, connection_manager
from app.main import app
from app.core.config import settings


class TestWebSocketService:
    """Test the WebSocket service interface"""

    def test_websocket_service_initialization(self):
        """Test that WebSocket service can be initialized"""
        service = websocket_service
        assert service is not None
        assert hasattr(service, "notify_item_created")
        assert hasattr(service, "notify_item_updated")
        assert hasattr(service, "notify_item_deleted")
        assert hasattr(service, "notify_list_updated")
        assert hasattr(service, "notify_list_shared")
        assert hasattr(service, "notify_list_deleted")

    @pytest.mark.asyncio
    async def test_notify_item_created(self):
        """Test item creation notification"""
        # Mock connection manager
        mock_manager = AsyncMock()
        websocket_service.set_connection_manager(mock_manager)

        # Test data
        list_id = 1
        item_data = {"id": 1, "name": "Test Item", "quantity": 1}
        user_id = "user123"

        # Call the service method
        await websocket_service.notify_item_created(list_id, item_data, user_id)

        # Verify the manager was called correctly
        mock_manager.broadcast_item_change.assert_called_once_with(
            list_id=list_id, event_type="created", item_data=item_data, user_id=user_id
        )

    @pytest.mark.asyncio
    async def test_notify_without_connection_manager(self):
        """Test that notifications work gracefully without connection manager"""
        # Create a service without connection manager
        from app.services.websocket_service import WebSocketService

        service = WebSocketService()

        # Should not raise an error
        await service.notify_item_created(1, {"id": 1}, "user123")
        await service.notify_list_updated(1, {"id": 1}, "user123")


class TestListConnectionManager:
    """Test the WebSocket connection manager"""

    def test_connection_manager_initialization(self):
        """Test that connection manager initializes correctly"""
        manager = ListConnectionManager()
        assert manager.websocket_registry == {}
        assert manager.list_connections == {}

    @pytest.mark.asyncio
    async def test_authenticate_user_valid_token(self):
        """Test user authentication with valid JWT token"""
        manager = ListConnectionManager()

        # Create a mock user
        mock_user = Mock()
        mock_user.id = 1
        mock_user.email = "test@example.com"

        # Mock session and query
        mock_session = Mock()
        mock_result = Mock()
        mock_result.scalars.return_value.first.return_value = mock_user
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Create a valid JWT token with audience claim (like fastapi-users does)
        token_data = {
            "sub": "1",
            "email": "test@example.com",
            "aud": "fastapi-users:auth",
        }
        token = jwt.encode(token_data, settings.SECRET_KEY, algorithm="HS256")

        # Test authentication
        with patch("app.api.v1.ws.notifications.select") as mock_select:
            user = await manager.authenticate_user(token, mock_session)
            assert user == mock_user

    @pytest.mark.asyncio
    async def test_authenticate_user_invalid_token(self):
        """Test user authentication with invalid JWT token"""
        manager = ListConnectionManager()
        mock_session = Mock()

        # Test with invalid token
        user = await manager.authenticate_user("invalid_token", mock_session)
        assert user is None

    @pytest.mark.asyncio
    async def test_authenticate_user_array_audience(self):
        """Test user authentication with JWT token having array audience claim"""
        manager = ListConnectionManager()

        # Mock user
        mock_user = Mock()
        mock_user.id = "1"
        mock_user.email = "test@example.com"

        # Mock session and query
        mock_session = Mock()
        mock_result = Mock()
        mock_result.scalars.return_value.first.return_value = mock_user
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Create a JWT token with ARRAY audience claim (like some fastapi-users configurations)
        token_data = {
            "sub": "1",
            "email": "test@example.com",
            "aud": ["fastapi-users:auth"],
        }
        token = jwt.encode(token_data, settings.SECRET_KEY, algorithm="HS256")

        # Test authentication
        with patch("app.api.v1.ws.notifications.select") as mock_select:
            user = await manager.authenticate_user(token, mock_session)
            assert user == mock_user

    @pytest.mark.asyncio
    async def test_authenticate_user_invalid_array_audience(self):
        """Test user authentication with JWT token having invalid array audience"""
        manager = ListConnectionManager()
        mock_session = Mock()

        # Create a JWT token with invalid array audience
        token_data = {
            "sub": "1",
            "email": "test@example.com",
            "aud": ["wrong-audience"],
        }
        token = jwt.encode(token_data, settings.SECRET_KEY, algorithm="HS256")

        # Test authentication should fail
        user = await manager.authenticate_user(token, mock_session)
        assert user is None

    @pytest.mark.asyncio
    async def test_authenticate_user_multiple_audiences(self):
        """Test user authentication with JWT token having multiple audiences including the valid one"""
        manager = ListConnectionManager()

        # Mock user
        mock_user = Mock()
        mock_user.id = "1"
        mock_user.email = "test@example.com"

        # Mock session and query
        mock_session = Mock()
        mock_result = Mock()
        mock_result.scalars.return_value.first.return_value = mock_user
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Create a JWT token with multiple audiences including the valid one
        token_data = {
            "sub": "1",
            "email": "test@example.com",
            "aud": ["other-service", "fastapi-users:auth", "another-service"],
        }
        token = jwt.encode(token_data, settings.SECRET_KEY, algorithm="HS256")

        # Test authentication should succeed
        with patch("app.api.v1.ws.notifications.select") as mock_select:
            user = await manager.authenticate_user(token, mock_session)
            assert user == mock_user

    @pytest.mark.asyncio
    async def test_verify_list_access_owner(self):
        """Test list access verification for list owner"""
        manager = ListConnectionManager()

        # Mock user and list
        mock_user = Mock()
        mock_user.id = 1

        mock_list = Mock()
        mock_list.owner_id = 1

        # Mock session and query
        mock_session = Mock()
        mock_result = Mock()
        mock_result.scalars.return_value.first.return_value = mock_list
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Test access verification
        with patch("app.api.v1.ws.notifications.select") as mock_select:
            has_access = await manager.verify_list_access(mock_user, 1, mock_session)
            assert has_access is True

    @pytest.mark.asyncio
    async def test_verify_list_access_no_access(self):
        """Test list access verification when user has no access"""
        manager = ListConnectionManager()

        # Mock user
        mock_user = Mock()
        mock_user.id = 1

        # Mock session that returns no list
        mock_session = Mock()
        mock_result = Mock()
        mock_result.scalars.return_value.first.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Test access verification
        with patch("app.api.v1.ws.notifications.select") as mock_select:
            has_access = await manager.verify_list_access(mock_user, 1, mock_session)
            assert has_access is False

    @pytest.mark.asyncio
    async def test_broadcast_item_change(self):
        """Test broadcasting item changes"""
        manager = ListConnectionManager()

        # Mock websocket
        mock_websocket = Mock()
        mock_websocket.send_text = AsyncMock()

        # Add connection
        manager.list_connections[1] = [(mock_websocket, "user123")]
        manager.websocket_registry[mock_websocket] = {
            "user_id": "user123",
            "list_id": 1,
        }

        # Broadcast item change
        await manager.broadcast_item_change(
            list_id=1,
            event_type="created",
            item_data={"id": 1, "name": "Test Item"},
            user_id="user456",  # Different user
        )

        # Verify websocket was called
        mock_websocket.send_text.assert_called_once()
        call_args = mock_websocket.send_text.call_args[0][0]
        message = json.loads(call_args)

        assert message["type"] == "item_change"
        assert message["event_type"] == "created"
        assert message["list_id"] == 1
        assert message["item"]["id"] == 1
        assert message["user_id"] == "user456"

    @pytest.mark.asyncio
    async def test_broadcast_excludes_sender(self):
        """Test that broadcasts exclude the sender"""
        manager = ListConnectionManager()

        # Mock websocket for sender
        mock_websocket = Mock()
        mock_websocket.send_text = AsyncMock()

        # Add connection for the sender
        manager.list_connections[1] = [(mock_websocket, "user123")]
        manager.websocket_registry[mock_websocket] = {
            "user_id": "user123",
            "list_id": 1,
        }

        # Broadcast with same user as sender
        await manager.broadcast_item_change(
            list_id=1,
            event_type="created",
            item_data={"id": 1, "name": "Test Item"},
            user_id="user123",  # Same user
        )

        # Verify websocket was NOT called (sender excluded)
        mock_websocket.send_text.assert_not_called()


class TestWebSocketIntegration:
    """Integration tests for WebSocket functionality"""

    @pytest.mark.asyncio
    async def test_websocket_connection_requires_authentication(self):
        """Test that WebSocket connections require valid authentication"""
        client = TestClient(app)

        # Try to connect without token
        with pytest.raises(Exception):
            with client.websocket_connect("/api/v1/ws/lists/1"):
                pass

        # Try to connect with invalid token
        with pytest.raises(Exception):
            with client.websocket_connect("/api/v1/ws/lists/1?token=invalid"):
                pass

    @pytest.mark.asyncio
    async def test_service_integration_with_endpoints(self):
        """Test that WebSocket service integrates correctly with API endpoints"""
        # Mock the connection manager
        mock_manager = AsyncMock()
        websocket_service.set_connection_manager(mock_manager)

        # This test would require a full integration setup with database
        # For now, just verify the service can be called
        await websocket_service.notify_item_created(
            list_id=1, item_data={"id": 1, "name": "Test Item"}, user_id="user123"
        )

        # Verify the manager method was called
        mock_manager.broadcast_item_change.assert_called_once()


# Fixtures for testing
@pytest.fixture
def mock_websocket():
    """Create a mock WebSocket for testing"""
    websocket = Mock(spec=WebSocket)
    websocket.send_text = AsyncMock()
    websocket.receive_text = AsyncMock()
    websocket.close = AsyncMock()
    return websocket


@pytest.fixture
def mock_user():
    """Create a mock user for testing"""
    user = Mock()
    user.id = 1
    user.email = "test@example.com"
    return user


@pytest.fixture
def connection_manager_with_connection(mock_websocket, mock_user):
    """Create a connection manager with an active connection"""
    manager = ListConnectionManager()

    # Add a connection
    list_id = 1
    user_id = str(mock_user.id)

    manager.list_connections[list_id] = [(mock_websocket, user_id)]
    manager.websocket_registry[mock_websocket] = {
        "user_id": user_id,
        "list_id": list_id,
    }

    return manager


@pytest.mark.asyncio
async def test_ping_pong_functionality(
    connection_manager_with_connection, mock_websocket
):
    """Test ping/pong functionality for connection keepalive"""
    manager = connection_manager_with_connection

    # Simulate ping message
    ping_message = {"type": "ping"}

    # This would normally be handled in the WebSocket endpoint
    # Test that the manager can send pong response
    await manager.send_to_websocket(
        mock_websocket, {"type": "pong", "timestamp": "2023-01-01T00:00:00"}
    )

    mock_websocket.send_text.assert_called_once()
    call_args = mock_websocket.send_text.call_args[0][0]
    message = json.loads(call_args)

    assert message["type"] == "pong"
    assert "timestamp" in message


@pytest.mark.asyncio
async def test_websocket_stability_no_reconnection_loop(self):
    """Test that WebSocket doesn't cause reconnection loops due to dependency changes"""
    manager = ListConnectionManager()

    # Mock user
    mock_user = Mock()
    mock_user.id = "1"
    mock_user.email = "test@example.com"
    mock_user.nickname = "TestUser"

    # Mock session and query
    mock_session = Mock()
    mock_result = Mock()
    mock_result.scalars.return_value.first.return_value = mock_user
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Create JWT token with array audience (the problematic format)
    token_data = {
        "sub": "1",
        "email": "test@example.com",
        "aud": ["fastapi-users:auth"],
    }
    token = jwt.encode(token_data, settings.SECRET_KEY, algorithm="HS256")

    # Test multiple authentication calls to ensure no dependency loops
    with patch("app.api.v1.ws.notifications.select") as mock_select:
        # First authentication
        user1 = await manager.authenticate_user(token, mock_session)
        assert user1 == mock_user

        # Second authentication with same token should work consistently
        user2 = await manager.authenticate_user(token, mock_session)
        assert user2 == mock_user

        # Third authentication to verify no state corruption
        user3 = await manager.authenticate_user(token, mock_session)
        assert user3 == mock_user

        # All calls should return the same user object
        assert user1 == user2 == user3
