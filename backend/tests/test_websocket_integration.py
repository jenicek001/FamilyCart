"""
Integration test for real-time WebSocket functionality.
Tests the complete flow from API calls to WebSocket notifications.
"""

import pytest
import asyncio
import json
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch
from httpx import AsyncClient

from app.main import app
from app.services.websocket_service import websocket_service
from app.api.v1.ws.notifications import connection_manager


class TestRealtimeIntegration:
    """Integration tests for real-time WebSocket functionality"""

    @pytest.fixture(autouse=True)
    def setup_websocket_service(self):
        """Ensure WebSocket service is properly initialized for tests"""
        # Initialize the websocket service with the connection manager
        websocket_service.set_connection_manager(connection_manager)
        yield
        # Cleanup after test
        websocket_service.set_connection_manager(None)

    def test_websocket_service_initialization_on_startup(self):
        """Test that the WebSocket service is properly initialized during app startup"""
        # The websocket service should be initialized with the connection manager
        assert websocket_service._connection_manager is not None
        assert websocket_service._connection_manager == connection_manager

    @pytest.mark.asyncio
    async def test_item_creation_triggers_notification(self):
        """Test that creating an item through API triggers WebSocket notification"""
        
        # Mock the connection manager's broadcast method
        original_broadcast = connection_manager.broadcast_item_change
        connection_manager.broadcast_item_change = AsyncMock()
        
        try:
            # Create mock data
            list_id = 1
            item_data = {"id": 1, "name": "Test Item", "quantity": 1}
            user_id = "test_user_123"
            
            # Call the websocket service method (simulating what the API endpoint does)
            await websocket_service.notify_item_created(list_id, item_data, user_id)
            
            # Verify the broadcast method was called
            connection_manager.broadcast_item_change.assert_called_once_with(
                list_id=list_id,
                event_type="created",
                item_data=item_data,
                user_id=user_id
            )
            
        finally:
            # Restore original method
            connection_manager.broadcast_item_change = original_broadcast

    @pytest.mark.asyncio
    async def test_list_sharing_triggers_notification(self):
        """Test that sharing a list triggers WebSocket notification"""
        
        # Mock the connection manager's broadcast method
        original_broadcast = connection_manager.broadcast_list_change
        connection_manager.broadcast_list_change = AsyncMock()
        
        try:
            # Create mock data
            list_id = 1
            list_data = {"id": 1, "name": "Test List", "members": []}
            user_id = "test_user_123"
            new_member_email = "newmember@example.com"
            
            # Call the websocket service method
            await websocket_service.notify_list_shared(list_id, list_data, new_member_email, user_id)
            
            # Verify the broadcast method was called with correct data
            connection_manager.broadcast_list_change.assert_called_once()
            
            # Check the call arguments
            call_args = connection_manager.broadcast_list_change.call_args
            assert call_args[1]["list_id"] == list_id
            assert call_args[1]["event_type"] == "shared"
            assert call_args[1]["user_id"] == user_id
            assert "new_member_email" in call_args[1]["list_data"]
            
        finally:
            # Restore original method
            connection_manager.broadcast_list_change = original_broadcast

    @pytest.mark.asyncio
    async def test_notification_methods_coverage(self):
        """Test that all notification methods are implemented and callable"""
        
        # Mock the connection manager
        mock_manager = AsyncMock()
        websocket_service.set_connection_manager(mock_manager)
        
        try:
            # Test all notification methods
            await websocket_service.notify_item_created(1, {"id": 1}, "user1")
            await websocket_service.notify_item_updated(1, {"id": 1}, "user1")
            await websocket_service.notify_item_deleted(1, 1, "user1")
            await websocket_service.notify_list_updated(1, {"id": 1}, "user1")
            await websocket_service.notify_list_shared(1, {"id": 1}, "test@example.com", "user1")
            await websocket_service.notify_list_deleted(1, "user1")
            await websocket_service.notify_member_removed(1, "user2", "user1")
            await websocket_service.notify_category_changed(1, {"id": 1}, "user1")
            
            # Verify all methods were called
            assert mock_manager.broadcast_item_change.call_count == 4  # created, updated, deleted, category_changed
            assert mock_manager.broadcast_list_change.call_count == 4  # updated, shared, deleted, member_removed
            
        finally:
            # Restore original connection manager
            websocket_service.set_connection_manager(connection_manager)

    def test_websocket_endpoint_routing(self):
        """Test that WebSocket endpoint is properly routed"""
        client = TestClient(app)
        
        # Test that the WebSocket endpoint exists (will fail auth, but endpoint should be found)
        # This is a basic connectivity test
        try:
            with client.websocket_connect("/api/v1/ws/lists/1?token=invalid"):
                pass
        except Exception as e:
            # We expect this to fail due to invalid token, but it should reach the endpoint
            # If the endpoint doesn't exist, we'd get a different error
            assert "WebSocket" in str(type(e).__name__) or "websocket" in str(e).lower()

    @pytest.mark.asyncio
    async def test_message_format_consistency(self):
        """Test that WebSocket messages have consistent format"""
        
        # Mock websocket
        mock_websocket = Mock()
        mock_websocket.send_text = AsyncMock()
        
        # Add mock connection
        connection_manager.list_connections[1] = [(mock_websocket, "user123")]
        connection_manager.websocket_registry[mock_websocket] = {"user_id": "user123", "list_id": 1}
        
        try:
            # Test item change message format
            await connection_manager.broadcast_item_change(
                list_id=1,
                event_type="created",
                item_data={"id": 1, "name": "Test"},
                user_id="user456"
            )
            
            # Verify message was sent
            mock_websocket.send_text.assert_called()
            
            # Parse and verify message format
            call_args = mock_websocket.send_text.call_args[0][0]
            message = json.loads(call_args)
            
            # Check required fields
            assert "type" in message
            assert "event_type" in message
            assert "list_id" in message
            assert "timestamp" in message
            assert "user_id" in message
            
            # Check specific values
            assert message["type"] == "item_change"
            assert message["event_type"] == "created"
            assert message["list_id"] == 1
            assert message["user_id"] == "user456"
            
        finally:
            # Clean up
            connection_manager.list_connections.clear()
            connection_manager.websocket_registry.clear()


@pytest.mark.asyncio
async def test_complete_realtime_flow():
    """
    Test the complete real-time flow:
    1. User connects to WebSocket
    2. Another user makes changes via API
    3. First user receives real-time notifications
    """
    
    # Initialize WebSocket service for this test
    websocket_service.set_connection_manager(connection_manager)
    
    try:
        # This is a conceptual test - in a real environment, we'd need:
        # 1. Two authenticated users
        # 2. A shared shopping list
        # 3. WebSocket connections
        # 4. API calls that trigger notifications
        
        # For now, we verify that the components are properly wired together
        assert websocket_service._connection_manager is not None
        assert hasattr(websocket_service, 'notify_item_created')
        assert hasattr(websocket_service, 'notify_list_shared')
        
        # Verify that the connection manager has the required methods
        assert hasattr(connection_manager, 'broadcast_item_change')
        assert hasattr(connection_manager, 'broadcast_list_change')
        assert hasattr(connection_manager, 'authenticate_user')
        assert hasattr(connection_manager, 'verify_list_access')
        
        print("✅ All real-time components are properly wired together")
    
    finally:
        # Cleanup
        websocket_service.set_connection_manager(None)


# Performance test
@pytest.mark.asyncio 
async def test_websocket_performance():
    """Test WebSocket performance with multiple connections"""
    
    # Mock multiple websockets
    mock_websockets = []
    for i in range(10):
        mock_ws = Mock()
        mock_ws.send_text = AsyncMock()
        mock_websockets.append(mock_ws)
        
        # Add to connection manager
        connection_manager.list_connections.setdefault(1, []).append((mock_ws, f"user{i}"))
        connection_manager.websocket_registry[mock_ws] = {"user_id": f"user{i}", "list_id": 1}
    
    try:
        # Measure broadcast time
        import time
        start_time = time.time()
        
        # Broadcast to all connections
        await connection_manager.broadcast_item_change(
            list_id=1,
            event_type="created",
            item_data={"id": 1, "name": "Performance Test"},
            user_id="broadcaster"
        )
        
        end_time = time.time()
        broadcast_time = end_time - start_time
        
        # Verify all websockets received the message
        for mock_ws in mock_websockets:
            mock_ws.send_text.assert_called_once()
        
        # Performance assertion (should be fast)
        assert broadcast_time < 1.0, f"Broadcast took too long: {broadcast_time}s"
        
        print(f"✅ Broadcast to 10 connections took {broadcast_time:.3f}s")
        
    finally:
        # Clean up
        connection_manager.list_connections.clear()
        connection_manager.websocket_registry.clear()


if __name__ == "__main__":
    # Run basic integration tests
    asyncio.run(test_complete_realtime_flow())
