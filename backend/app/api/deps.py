from typing import AsyncGenerator

from fastapi import Depends, HTTPException
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import AsyncSessionLocal, get_session
from app.models.user import User


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