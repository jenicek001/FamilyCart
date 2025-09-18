from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status, Query, Depends
from typing import Dict, List, Optional, Set
import json
import jwt
import logging
import uuid
from datetime import datetime, UTC
from uuid import UUID

from app.core.config import settings
from app.models import User
from app.api.deps import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

logger = logging.getLogger(__name__)
router = APIRouter()


class UUIDJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles UUID objects"""

    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        return super().default(obj)


class ListConnectionManager:
    """
    Enhanced WebSocket connection manager for shopping list real-time updates.
    Manages connections per shopping list (room-based) with JWT authentication.
    Uses session IDs to enable same-user multi-device synchronization.
    """

    def __init__(self):
        # Dictionary mapping list_id -> set of (websocket, user_id, session_id) tuples
        self.list_connections: Dict[int, Set[tuple]] = {}
        # Dictionary mapping websocket -> (user_id, list_id, session_id) for cleanup
        self.websocket_registry: Dict[WebSocket, tuple] = {}
        # Dictionary mapping session_id -> websocket for session-based exclusion
        self.session_registry: Dict[str, WebSocket] = {}

    async def authenticate_user(
        self, token: str, session: AsyncSession
    ) -> Optional[User]:
        """Authenticate user from JWT token"""
        try:
            # First try to decode without audience validation to check the token structure
            unverified_payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
                options={"verify_aud": False},
            )

            # Get the audience from the token to handle both string and array formats
            token_audience = unverified_payload.get("aud")
            expected_audience = "fastapi-users:auth"

            # Validate audience manually to handle both string and array formats
            if isinstance(token_audience, list):
                if expected_audience not in token_audience:
                    logger.warning(
                        f"JWT audience validation failed: expected '{expected_audience}' in {token_audience}"
                    )
                    return None
            elif isinstance(token_audience, str):
                if token_audience != expected_audience:
                    logger.warning(
                        f"JWT audience validation failed: expected '{expected_audience}', got '{token_audience}'"
                    )
                    return None
            else:
                logger.warning(
                    f"JWT audience validation failed: invalid audience format {type(token_audience)}"
                )
                return None

            # Now decode with proper audience validation (using the format from the token)
            if isinstance(token_audience, list):
                # If token has array audience, validate against the array
                payload = jwt.decode(
                    token,
                    settings.SECRET_KEY,
                    algorithms=[settings.ALGORITHM],
                    audience=token_audience,
                )
            else:
                # If token has string audience, validate against the string
                payload = jwt.decode(
                    token,
                    settings.SECRET_KEY,
                    algorithms=[settings.ALGORITHM],
                    audience=expected_audience,
                )

            user_id: str = payload.get("sub")
            if not user_id:
                logger.warning("JWT token missing 'sub' claim")
                return None

            # Get user from database
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalars().first()

            if not user:
                logger.warning(f"User with ID {user_id} not found in database")
                return None

            return user
        except jwt.PyJWTError as e:
            logger.warning(f"JWT authentication failed: {e}")
            return None

    async def verify_list_access(
        self, user: User, list_id: int, session: AsyncSession
    ) -> bool:
        """Check if user has access to the shopping list"""
        from app.models import ShoppingList

        # Check if user owns the list or it's shared with them
        result = await session.execute(
            select(ShoppingList).where(
                ShoppingList.id == list_id, ShoppingList.owner_id == user.id
            )
        )
        if result.scalars().first():
            return True

        # Check if list is shared with user
        result = await session.execute(
            select(ShoppingList)
            .where(ShoppingList.id == list_id)
            .join(ShoppingList.shared_with.and_(User.id == user.id))
        )
        return result.scalars().first() is not None

    async def connect(self, websocket: WebSocket, user: User, list_id: int):
        """Connect user to a specific shopping list room with session tracking"""
        await websocket.accept()

        # Generate unique session ID for this connection
        session_id = str(uuid.uuid4())

        # Add to list connections
        if list_id not in self.list_connections:
            self.list_connections[list_id] = set()

        connection_tuple = (websocket, user.id, session_id)
        self.list_connections[list_id].add(connection_tuple)

        # Register websocket for cleanup
        self.websocket_registry[websocket] = (user.id, list_id, session_id)

        # Register session for session-based exclusion
        self.session_registry[session_id] = websocket

        logger.info(
            f"User {user.nickname} connected to list {list_id} with session {session_id}"
        )

        # Send welcome message with session ID
        await self.send_to_websocket(
            websocket,
            {
                "type": "connection_established",
                "message": f"Connected to list {list_id}",
                "session_id": session_id,
                "timestamp": datetime.now(UTC).isoformat(),
            },
        )

    async def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection from the manager"""
        if websocket in self.websocket_registry:
            registry_data = self.websocket_registry[websocket]
            if len(registry_data) == 3:
                user_id, list_id, session_id = registry_data
            else:
                # Handle legacy format if exists
                user_id, list_id = registry_data
                session_id = "unknown"

            self.websocket_registry.pop(websocket)

            # Remove from connections
            if list_id in self.list_connections:
                # Remove the tuple with this websocket
                self.list_connections[list_id] = {
                    conn
                    for conn in self.list_connections[list_id]
                    if conn[0] != websocket
                }

                # Clean up empty sets
                if not self.list_connections[list_id]:
                    del self.list_connections[list_id]

            # Remove from session registry (only if we have a valid session_id)
            if session_id != "unknown" and session_id in self.session_registry:
                del self.session_registry[session_id]

            logger.info(
                f"User {user_id} disconnected from list {list_id} (session {session_id})"
            )
        else:
            logger.warning(
                "Attempted to disconnect a websocket that was not in the registry"
            )

    async def send_to_websocket(self, websocket: WebSocket, data: dict):
        """Send data to a specific websocket with proper UUID serialization"""
        try:
            json_data = json.dumps(data, cls=UUIDJSONEncoder)
            await websocket.send_text(json_data)
        except Exception as e:
            logger.error(f"Error sending to websocket: {e}")
            # Log the data that failed to serialize for debugging
            logger.debug(f"Failed data: {data}")

    async def broadcast_to_list(
        self,
        list_id: int,
        data: dict,
        exclude_user_id: Optional[str] = None,
        exclude_websocket: Optional[WebSocket] = None,
        exclude_session_id: Optional[str] = None,
    ):
        """Broadcast message to all users connected to a specific list"""
        if list_id not in self.list_connections:
            return

        disconnected_websockets = []

        for websocket, user_id, session_id in list(self.list_connections[list_id]):
            # Skip the specific session that triggered the update (for same-user multi-device sync)
            if exclude_session_id and session_id == exclude_session_id:
                continue

            # Skip the specific websocket connection that triggered the update
            if exclude_websocket and websocket == exclude_websocket:
                continue

            # Legacy: Skip the user who triggered the update (deprecated - use exclude_session_id instead)
            if (
                exclude_user_id
                and user_id == exclude_user_id
                and exclude_session_id is None
                and exclude_websocket is None
            ):
                continue

            try:
                await self.send_to_websocket(websocket, data)
            except Exception as e:
                logger.error(
                    f"Error broadcasting to user {user_id} (session {session_id}): {e}"
                )
                disconnected_websockets.append(websocket)

        # Clean up disconnected websockets
        for websocket in disconnected_websockets:
            await self.disconnect(websocket)

    async def broadcast_item_change(
        self,
        list_id: int,
        event_type: str,
        item_data: dict,
        user_id: str,
        exclude_websocket: Optional[WebSocket] = None,
        exclude_session_id: Optional[str] = None,
        exclude_user_id: Optional[str] = None,
    ):
        """Broadcast item changes to list members"""
        message = {
            "type": "item_change",
            "event_type": event_type,  # "created", "updated", "deleted"
            "list_id": list_id,
            "item": item_data,
            "timestamp": datetime.now(UTC).isoformat(),
            "user_id": user_id,
        }
        await self.broadcast_to_list(
            list_id,
            message,
            exclude_websocket=exclude_websocket,
            exclude_session_id=exclude_session_id,
            exclude_user_id=exclude_user_id,
        )

    async def broadcast_list_change(
        self,
        list_id: int,
        event_type: str,
        list_data: dict,
        user_id: str,
        exclude_websocket: Optional[WebSocket] = None,
        exclude_session_id: Optional[str] = None,
        exclude_user_id: Optional[str] = None,
    ):
        """Broadcast list changes to list members"""
        message = {
            "type": "list_change",
            "event_type": event_type,  # "updated", "shared", "member_removed"
            "list_id": list_id,
            "list": list_data,
            "timestamp": datetime.now(UTC).isoformat(),
            "user_id": user_id,
        }
        await self.broadcast_to_list(
            list_id,
            message,
            exclude_websocket=exclude_websocket,
            exclude_session_id=exclude_session_id,
            exclude_user_id=exclude_user_id,
        )


# Global connection manager instance
connection_manager = ListConnectionManager()


@router.websocket("/lists/{list_id}")
async def websocket_list_endpoint(
    websocket: WebSocket,
    list_id: int,
    token: str = Query(...),
    session: AsyncSession = Depends(get_session),
):
    """
    WebSocket endpoint for real-time updates on a specific shopping list.
    Requires JWT authentication via query parameter.
    """
    # Authenticate user
    user = await connection_manager.authenticate_user(token, session)
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # Verify list access
    has_access = await connection_manager.verify_list_access(user, list_id, session)
    if not has_access:
        await websocket.close(code=status.WS_1003_UNSUPPORTED_DATA)
        return

    # Connect to list room
    await connection_manager.connect(websocket, user, list_id)

    try:
        while True:
            # Handle incoming messages (ping/pong, heartbeat)
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await connection_manager.send_to_websocket(
                        websocket,
                        {"type": "pong", "timestamp": datetime.now(UTC).isoformat()},
                    )
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON from user {user.id}: {data}")

    except WebSocketDisconnect:
        # Normal disconnection - no need to log as error
        logger.info(f"User {user.id} disconnected from list {list_id}")
        await connection_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error for user {user.id}: {e}")
        await connection_manager.disconnect(websocket)
        await connection_manager.disconnect(websocket)


# Export the connection manager for use in other parts of the application
__all__ = ["connection_manager", "router"]
