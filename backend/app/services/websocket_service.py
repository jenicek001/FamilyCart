"""
WebSocket service for broadcasting real-time updates across the application.
This service integrates with API endpoints to send real-time notifications.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class WebSocketService:
    """
    Service class for managing WebSocket notifications.
    This provides a clean interface for other parts of the application
    to send real-time updates without directly coupling to WebSocket code.
    """

    def __init__(self):
        self._connection_manager = None

    def set_connection_manager(self, manager):
        """Set the connection manager (called during app startup)"""
        self._connection_manager = manager

    async def notify_item_created(
        self, list_id: int, item_data: Dict[str, Any], user_id: str
    ):
        """Notify list members that a new item was created"""
        if not self._connection_manager:
            return

        await self._connection_manager.broadcast_item_change(
            list_id=list_id, event_type="created", item_data=item_data, user_id=user_id
        )
        logger.info(f"Broadcast item creation to list {list_id}")

    async def notify_item_updated(
        self, list_id: int, item_data: Dict[str, Any], user_id: str
    ):
        """Notify list members that an item was updated"""
        if not self._connection_manager:
            return

        await self._connection_manager.broadcast_item_change(
            list_id=list_id, event_type="updated", item_data=item_data, user_id=user_id
        )
        logger.info(f"Broadcast item update to list {list_id}")

    async def notify_item_deleted(self, list_id: int, item_id: int, user_id: str):
        """Notify list members that an item was deleted"""
        if not self._connection_manager:
            return

        await self._connection_manager.broadcast_item_change(
            list_id=list_id,
            event_type="deleted",
            item_data={"id": item_id},
            user_id=user_id,
        )
        logger.info(f"Broadcast item deletion to list {list_id}")

    async def notify_list_updated(
        self, list_id: int, list_data: Dict[str, Any], user_id: str
    ):
        """Notify list members that list details were updated"""
        if not self._connection_manager:
            return

        await self._connection_manager.broadcast_list_change(
            list_id=list_id, event_type="updated", list_data=list_data, user_id=user_id
        )
        logger.info(f"Broadcast list update to list {list_id}")

    async def notify_list_shared(
        self,
        list_id: int,
        list_data: Dict[str, Any],
        new_member_email: str,
        user_id: str,
    ):
        """Notify list members that the list was shared with someone new"""
        if not self._connection_manager:
            return

        list_data_with_member = {**list_data, "new_member_email": new_member_email}

        await self._connection_manager.broadcast_list_change(
            list_id=list_id,
            event_type="shared",
            list_data=list_data_with_member,
            user_id=user_id,
        )
        logger.info(f"Broadcast list sharing to list {list_id}")

    async def notify_member_removed(
        self, list_id: int, removed_user_id: str, user_id: str
    ):
        """Notify list members that someone was removed from the list"""
        if not self._connection_manager:
            return

        await self._connection_manager.broadcast_list_change(
            list_id=list_id,
            event_type="member_removed",
            list_data={"removed_user_id": removed_user_id},
            user_id=user_id,
        )
        logger.info(f"Broadcast member removal from list {list_id}")

    async def notify_list_deleted(self, list_id: int, user_id: str):
        """Notify list members that the list was deleted"""
        if not self._connection_manager:
            return

        await self._connection_manager.broadcast_list_change(
            list_id=list_id,
            event_type="deleted",
            list_data={"id": list_id},
            user_id=user_id,
        )
        logger.info(f"Broadcast list deletion to list {list_id}")

    async def notify_category_changed(
        self, list_id: int, item_data: Dict[str, Any], user_id: str
    ):
        """Notify list members that an item's category was changed"""
        if not self._connection_manager:
            return

        await self._connection_manager.broadcast_item_change(
            list_id=list_id,
            event_type="category_changed",
            item_data=item_data,
            user_id=user_id,
        )
        logger.info(f"Broadcast category change to list {list_id}")


# Global WebSocket service instance
websocket_service = WebSocketService()
