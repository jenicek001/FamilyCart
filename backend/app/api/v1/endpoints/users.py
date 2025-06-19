from fastapi import APIRouter

from app.api.v1.endpoints.auth import fastapi_users
from app.schemas.user import UserRead, UserUpdate

router = APIRouter()

router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

