"""
WebSocket notification helpers for shopping list operations.
"""

import logging
from typing import Any, Dict

from app.services.websocket_service import websocket_service

logger = logging.getLogger(__name__)


class WebSocketNotifier:
    """Service for sending WebSocket notifications."""

    @staticmethod
    async def notify_item_created(
        list_id: int, item_data: Dict[str, Any], user_id: str
    ):
        """Send notification when an item is created."""
        try:
            await websocket_service.notify_item_created(
                list_id=list_id, item_data=item_data, user_id=user_id
            )
        except Exception as e:
            logger.error(
                f"Failed to send WebSocket notification for item creation: {e}"
            )
            logger.exception("Full exception details:")

    @staticmethod
    async def notify_item_updated(
        list_id: int, item_data: Dict[str, Any], user_id: str
    ):
        """Send notification when an item is updated."""
        try:
            await websocket_service.notify_item_updated(
                list_id=list_id, item_data=item_data, user_id=user_id
            )
        except Exception as e:
            logger.error(f"Failed to send WebSocket notification for item update: {e}")
            logger.exception("Full exception details:")

    @staticmethod
    async def notify_item_deleted(list_id: int, item_id: int, user_id: str):
        """Send notification when an item is deleted."""
        try:
            await websocket_service.notify_item_deleted(
                list_id=list_id, item_id=item_id, user_id=user_id
            )
        except Exception as e:
            logger.error(
                f"Failed to send WebSocket notification for item deletion: {e}"
            )
            logger.exception("Full exception details:")

    @staticmethod
    async def notify_list_updated(
        list_id: int, list_data: Dict[str, Any], user_id: str
    ):
        """Send notification when a list is updated."""
        try:
            await websocket_service.notify_list_updated(
                list_id=list_id, list_data=list_data, user_id=user_id
            )
        except Exception as e:
            logger.error(f"Failed to send WebSocket notification for list update: {e}")
            logger.exception("Full exception details:")

    @staticmethod
    async def notify_list_deleted(list_id: int, user_id: str):
        """Send notification when a list is deleted."""
        try:
            await websocket_service.notify_list_deleted(
                list_id=list_id, user_id=user_id
            )
        except Exception as e:
            logger.error(
                f"Failed to send WebSocket notification for list deletion: {e}"
            )
            logger.exception("Full exception details:")
