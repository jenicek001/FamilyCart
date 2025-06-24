"""
Special route handler to avoid trailing slash redirects.
This ensures that requests to "/api/v1/shopping-lists" (no trailing slash)
work correctly without causing 307 redirects that might lose headers.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.models.user import User
from app.core.fastapi_users import current_user
from app.schemas.shopping_list import ShoppingListRead, ShoppingListCreate
from app.api.deps import get_session
from app.api.v1.endpoints.shopping_lists import read_shopping_lists, create_shopping_list

logger = logging.getLogger(__name__)

router = APIRouter()

# Register handler for /api/v1/shopping-lists (no trailing slash)
@router.get("", response_model=List[ShoppingListRead])
async def get_shopping_lists_no_slash(
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(current_user)
):
    """
    Special handler for /api/v1/shopping-lists without trailing slash
    to avoid 307 redirects that lose auth headers.
    """
    logger.info(f"No-slash GET endpoint called by {current_user.email}")
    logger.info(f"Request headers: {request.headers}")
    
    # Call the original handler directly
    return await read_shopping_lists(session=session, current_user=current_user)

# Register POST handler for /api/v1/shopping-lists (no trailing slash)
@router.post("", response_model=ShoppingListRead)
async def create_shopping_list_no_slash(
    *,
    request: Request,
    session: AsyncSession = Depends(get_session),
    list_in: ShoppingListCreate,
    current_user: User = Depends(current_user),
):
    """
    Special handler for POST /api/v1/shopping-lists without trailing slash
    to avoid 307 redirects that lose auth headers.
    """
    logger.info(f"No-slash POST endpoint called by {current_user.email}")
    logger.info(f"Request headers: {request.headers}")
    
    # Call the original handler directly
    return await create_shopping_list(session=session, list_in=list_in, current_user=current_user)
