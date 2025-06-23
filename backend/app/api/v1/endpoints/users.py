from fastapi import APIRouter

from app.core.fastapi_users import fastapi_users
from app.schemas.user import UserRead, UserUpdate

router = APIRouter()

# User management routes (get user details, update user, delete user)
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    tags=["users"],
)

