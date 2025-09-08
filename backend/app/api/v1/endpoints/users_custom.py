from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from app.core.fastapi_users import fastapi_users, current_user
from app.models.user import User
from app.schemas.user import UserRead, UserUpdate

router = APIRouter()


# Add custom routes for the /me endpoint using built-in fastapi-users dependencies
@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(user: User = Depends(current_user)):
    """
    Delete the current authenticated user.
    """
    await fastapi_users.user_manager.delete(user)
    return None


@router.put("/me", response_model=UserRead)
async def update_current_user(
    user_update: UserUpdate, user: User = Depends(current_user)
):
    """
    Update the current authenticated user with PUT method (maps to PATCH).
    """
    return await fastapi_users.user_manager.update(user_update, user)
