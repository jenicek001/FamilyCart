from typing import AsyncGenerator

from app.core.config import settings
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import DeclarativeBase  # Corrected import

# Create the SQLAlchemy async engine
# Reason: Using async engine for compatibility with FastAPI async routes
engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI_ASYNC, echo=True) # echo=True for debugging, can be removed in production

# Create a configured "AsyncSession" class
# Reason: Using async_sessionmaker for async database sessions
AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession # Specify AsyncSession class
)

# Create a base class for our models
class Base(DeclarativeBase):
    """Base class for all database models."""
    pass

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function that yields async database sessions.
    
    Yields:
        AsyncSession: An async database session.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Import all models here for Alembic to discover them
# This is now handled by app.models.__init__.py, which should be imported in env.py
# from app.models import * # This would also work if __all__ is defined in app.models.__init__.py
