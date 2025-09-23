"""
Response builders for shopping list endpoints.
"""

import logging
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.models.shopping_list import ShoppingList
from app.schemas.item import ItemRead
from app.schemas.shopping_list import ShoppingListRead
from app.schemas.user import UserRead

from ..helpers import shopping_list_helpers as helpers

logger = logging.getLogger(__name__)


class ResponseBuilder:
    """Service for building endpoint responses."""

    @staticmethod
    async def build_list_response(
        shopping_list: ShoppingList, session: AsyncSession, current_user: User
    ) -> ShoppingListRead:
        """Build a shopping list response."""
        return await helpers.build_shopping_list_response(
            shopping_list, session, current_user
        )

    @staticmethod
    async def build_lists_response(
        shopping_lists: List[ShoppingList], current_user: User
    ) -> List[ShoppingListRead]:
        """Build response for multiple shopping lists."""
        result_models = []
        for l in shopping_lists:
            # Sort items by category before converting to Pydantic models
            sorted_items = helpers.sort_items_by_category(l.items) if l.items else []
            items = [
                ItemRead.model_validate(i, from_attributes=True) for i in sorted_items
            ]
            # Members: shared_with + owner if not already included
            members = [
                UserRead.model_validate(u, from_attributes=True) for u in l.shared_with
            ]
            if l.owner_id != current_user.id:
                members.append(UserRead.model_validate(l.owner, from_attributes=True))
            result_models.append(
                ShoppingListRead(
                    id=l.id,
                    name=l.name,
                    description=l.description,
                    owner_id=l.owner_id,
                    created_at=l.created_at,
                    updated_at=l.updated_at,
                    items=items,
                    members=members,
                )
            )
        return result_models
