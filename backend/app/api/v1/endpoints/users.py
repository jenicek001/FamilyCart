from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_current_user
from app.core.fastapi_users import fastapi_users
from app.core.users import UserManager, get_user_manager
from app.models.user import User
from app.schemas.user import UserRead, UserUpdate

router = APIRouter()

# User management routes (get user details, update user, delete user)
# Allow unverified users to access their own profile (so they can see they are unverified)
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate, requires_verification=False),
    prefix="/users",  # This creates the /users/me endpoint
    tags=["users"],
)


@router.delete("/users/me", status_code=status.HTTP_204_NO_CONTENT, tags=["users"])
async def delete_current_user(
    user: User = Depends(get_current_user),
    user_manager: UserManager = Depends(get_user_manager),
):
    """
    Delete the current authenticated user.
    """
    await user_manager.delete(user)
    return None


@router.put("/users/me", response_model=UserRead, tags=["users"])
async def update_current_user(
    user_update: UserUpdate,
    user: User = Depends(get_current_user),
    user_manager: UserManager = Depends(get_user_manager),
):
    """
    Update the current authenticated user with PUT method (maps to PATCH).
    """
    return await user_manager.update(user_update, user)
