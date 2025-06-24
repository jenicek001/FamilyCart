"""
Base configuration and fixtures for tests.
"""
import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.db.session import get_session
from app.core.config import settings
from app.models.user import User

# Create a test database engine
test_engine = create_async_engine(settings.DATABASE_URL + "_test")
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine, class_=AsyncSession)

# Create the test application
@pytest.fixture
def app() -> FastAPI:
    from app.main import app
    return app

@pytest.fixture
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database and yield the session, then clean up."""
    async with TestingSessionLocal() as session:
        yield session

@pytest.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client for the FastAPI application."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
async def test_user(test_db: AsyncSession) -> User:
    """Create a test user in the database."""
    test_user = User(
        email="testuser@example.com",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
        first_name="Test",
        last_name="User",
        is_active=True,
        is_superuser=False
    )
    test_db.add(test_user)
    await test_db.commit()
    await test_db.refresh(test_user)
    return test_user

@pytest.fixture
async def token_header(client: AsyncClient, test_user: User) -> dict:
    """Create an authentication token for the test user."""
    response = await client.post(
        "/api/v1/auth/jwt/login",
        data={"username": test_user.email, "password": "password"}
    )
    data = response.json()
    return {"Authorization": f"Bearer {data['access_token']}"}
