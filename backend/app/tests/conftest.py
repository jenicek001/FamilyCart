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

# Create a test database engine
# Replace the database name in the connection string
test_db_uri = settings.SQLALCHEMY_DATABASE_URI_ASYNC
if test_db_uri.endswith("/familycart"):
    test_db_uri = test_db_uri[:-len("/familycart")] + "/familycart_test"
test_engine = create_async_engine(test_db_uri)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine, class_=AsyncSession)

# Create the test application
@pytest.fixture(scope="function")
def app() -> FastAPI:
    from app.main import app
    return app

@pytest.fixture(scope="function")
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async with TestingSessionLocal() as session:
        yield session

@pytest.fixture(scope="function")
async def client(app: FastAPI, test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client for the FastAPI application."""
    def get_test_db():
        return test_db
    
    app.dependency_overrides[get_session] = get_test_db
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
async def test_user(client: AsyncClient) -> dict:
    """Create a test user via the registration endpoint."""
    import uuid
    
    # Generate unique user data
    unique_id = uuid.uuid4().hex[:8]
    test_email = f"testuser-{unique_id}@example.com"
    test_nickname = f"TestUser-{unique_id}"
    test_password = "TestPassword123!"
    
    # Register the user via the API
    register_data = {
        "email": test_email,
        "password": test_password,
        "first_name": "Test",
        "last_name": "User",
        "nickname": test_nickname
    }
    
    response = await client.post("/api/v1/auth/register", json=register_data)
    
    if response.status_code != 201:
        raise Exception(f"User registration failed: {response.status_code} - {response.text}")
    
    # Return the user data (not the User object, but the test credentials)
    user_data = response.json()
    user_data["password"] = test_password  # Add password for login
    return user_data

@pytest.fixture(scope="function")
async def token_header(client: AsyncClient, test_user: dict) -> dict:
    """Create an authentication token for the test user."""
    response = await client.post(
        "/api/v1/auth/jwt/login",
        data={"username": test_user["email"], "password": test_user["password"]},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    print(f"Login response status: {response.status_code}")
    print(f"Login response body: {response.text}")
    
    if response.status_code != 200:
        raise Exception(f"Login failed: {response.text}")
    
    data = response.json()
    return {"Authorization": f"Bearer {data['access_token']}"}
