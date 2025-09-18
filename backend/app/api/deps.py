from typing import AsyncGenerator, Optional

from fastapi import Depends, HTTPException, Header
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import AsyncSessionLocal, get_session
from app.models.user import User
from app.services.websocket_service import websocket_service


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get an async database session.
    """
    async with AsyncSessionLocal() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_session)):
    """
    Dependency to get the user database.
    """
    yield SQLAlchemyUserDatabase(session, User)


async def set_session_context(
    x_session_id: Optional[str] = Header(None, alias="x-session-id")
):
    """
    Extract session ID from request headers and set it in WebSocket service context.
    This enables session-specific exclusion for real-time updates.
    """
    if x_session_id:
        websocket_service.set_current_session_id(x_session_id)
    else:
        websocket_service.set_current_session_id(None)

    return x_session_id
