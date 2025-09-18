from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

# This check is important to ensure that the database URI is set
# before creating an engine.
if not settings.SQLALCHEMY_DATABASE_URI_ASYNC:
    raise ValueError(
        "SQLALCHEMY_DATABASE_URI_ASYNC is not set. Please check your .env file."
    )

engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI_ASYNC, pool_pre_ping=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
