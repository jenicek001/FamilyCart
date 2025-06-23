from fastapi import APIRouter

from app.core.auth import auth_backend
from app.core.fastapi_users import fastapi_users
from app.schemas.user import UserCreate, UserRead

router = APIRouter()

# Auth routes
router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/jwt",
    tags=["auth"],
)

# Register routes
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="",
    tags=["auth"],
)

# Reset password routes
router.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="",
    tags=["auth"],
)

# Verify routes
router.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="",
    tags=["auth"],
)

