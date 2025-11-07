from typing import AsyncGenerator, Optional

from fastapi import Depends, Header, HTTPException
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import AsyncSessionLocal, get_session
from app.models.shopping_list import ShoppingList
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


async def get_shopping_list(
    list_id: int, session: AsyncSession, current_user: User
) -> ShoppingList:
    """
    Helper function to retrieve a ShoppingList by ID,
    ensuring current_user is owner or shared member.
    """
    result = await session.execute(
        select(ShoppingList)
        .where(ShoppingList.id == list_id)
        .options(
            selectinload(ShoppingList.shared_with),
            selectinload(ShoppingList.items),
            selectinload(ShoppingList.owner),
        )
    )
    shopping_list = result.scalars().first()

    if not shopping_list:
        raise HTTPException(status_code=404, detail="Shopping list not found")

    # Check if user is owner or shared member
    if (
        shopping_list.owner_id != current_user.id
        and current_user not in shopping_list.shared_with
    ):
        raise HTTPException(status_code=403, detail="Access denied")

    return shopping_list
