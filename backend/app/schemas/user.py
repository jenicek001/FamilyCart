"""
Pydantic schemas for User model, compatible with fastapi-users.
"""

from typing import Optional
from uuid import UUID

from fastapi_users import schemas


class UserRead(schemas.BaseUser[UUID]):
    """Schema for reading user information."""

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    nickname: Optional[str] = None

    class Config:
        from_attributes = True  # Replaces orm_mode = True in Pydantic v2
        # Serialize UUIDs as strings to avoid JSON serialization issues
        json_encoders = {UUID: str}


class UserCreate(schemas.BaseUserCreate):
    """Schema for creating a new user."""

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    nickname: str  # Made mandatory


class UserUpdate(schemas.BaseUserUpdate):
    """Schema for updating an existing user."""

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    nickname: Optional[str] = None
