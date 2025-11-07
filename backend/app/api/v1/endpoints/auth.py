from fastapi import APIRouter

from app.core.auth import auth_backend
from app.core.fastapi_users import fastapi_users
from app.schemas.user import UserCreate, UserRead

router = APIRouter(prefix="/auth")  # Add /auth prefix to the entire router

# Auth routes - login, logout, etc.
router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/jwt",
    tags=["auth"],
)

# Register routes - used by the frontend for signup
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    tags=["auth"],
)

# Reset password routes
router.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/reset-password",
    tags=["auth"],
)

# Email verification routes
router.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/verify",
    tags=["auth"],
)
