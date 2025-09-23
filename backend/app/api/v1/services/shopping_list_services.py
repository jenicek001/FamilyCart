"""Business logic services for shopping list operations."""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.models.category import Category
from app.models.item import Item
from app.models.shopping_list import ShoppingList
from app.schemas.item import ItemCreate
from app.services.ai_service import ai_service
from app.services.notification_service import send_list_invitation_email
from app.services.websocket_service import websocket_service

logger = logging.getLogger(__name__)


class ItemCreationService:
    """Service for creating items with AI enhancement."""
    
    @staticmethod
    async def process_item_with_ai(
        item_name: str, 
        session: AsyncSession
    ) -> Tuple[Optional[Category], Optional[str], Dict, Optional[str]]:
        """
        Process item with AI to get category, standardized name, translations, and icon.
        Returns: (category, standardized_name, translations, icon_name)
        """
        category = None
        standardized_name = None
        translations = {}
        icon_name = None

        try:
            # Get existing categories for AI context
            categories_result = await session.execute(select(Category))
            existing_categories = categories_result.scalars().all()
            category_names = [cat.name for cat in existing_categories]

            # Run AI calls in parallel with timeout
            category_task = asyncio.create_task(
                ai_service.suggest_category_async(item_name, category_names)
            )
            translation_task = asyncio.create_task(
                ai_service.standardize_and_translate_item_name(item_name)
            )

            # Wait for both with timeout (max 15 seconds total)
            try:
                category_name, standardization_result = await asyncio.wait_for(
                    asyncio.gather(category_task, translation_task, return_exceptions=True),
                    timeout=15.0,
                )

                # Handle category result
                if isinstance(category_name, Exception):
                    logger.error(f"Category suggestion failed: {category_name}")
                    category_name = None
                elif category_name:
                    from app.api.v1.helpers.shopping_list_helpers import get_or_create_category
                    category = await get_or_create_category(category_name, session)

                # Handle translation result
                if isinstance(standardization_result, Exception):
                    logger.error(f"Translation failed: {standardization_result}")
                    standardization_result = {}

                standardized_name = (
                    standardization_result.get("standardized_name")
                    if standardization_result
                    else None
                )
                translations = (
                    standardization_result.get("translations", {})
                    if standardization_result
                    else {}
                )

                # Get icon suggestion only if we have a category
                if category:
                    try:
                        icon_name = await asyncio.wait_for(
                            ai_service.suggest_icon(item_name, category.name),
                            timeout=10.0,
                        )
                    except asyncio.TimeoutError:
                        logger.warning(f"Icon suggestion timed out for item '{item_name}'")
                        icon_name = "shopping_cart"
                    except Exception as e:
                        logger.error(f"Icon suggestion failed: {e}")
                        icon_name = "shopping_cart"

            except asyncio.TimeoutError:
                logger.warning(
                    f"AI processing timed out for item '{item_name}' - using fallbacks"
                )

        except Exception as e:
            logger.error(f"Error in AI processing for item '{item_name}': {e}")

        return category, standardized_name, translations, icon_name

    @staticmethod
    async def create_item_for_shopping_list(
        shopping_list: ShoppingList,
        item_in: ItemCreate,
        current_user: User,
        session: AsyncSession
    ) -> Item:
        """Create a new item for a shopping list with AI enhancement."""
        # Extract values from item_in
        item_name = item_in.name
        item_quantity = item_in.quantity
        item_comment = item_in.comment
        item_category_name = item_in.category_name
        item_icon_name = getattr(item_in, "icon_name", None)
        item_quantity_value = item_in.quantity_value
        item_quantity_unit_id = item_in.quantity_unit_id
        item_quantity_display_text = item_in.quantity_display_text

        # Process with AI
        category, standardized_name, translations, icon_name = await ItemCreationService.process_item_with_ai(
            item_name, session
        )

        # Use original category name if provided and no AI suggestion
        if not category and item_category_name:
            from app.api.v1.helpers.shopping_list_helpers import get_or_create_category
            category = await get_or_create_category(item_category_name, session)

        # Create item with AI-enhanced data
        final_name = standardized_name if standardized_name else item_name
        final_icon = item_icon_name if item_icon_name else (icon_name if icon_name else "shopping_cart")

        item = Item(
            name=final_name,
            quantity=item_quantity,
            comment=item_comment,
            shopping_list_id=shopping_list.id,
            owner_id=current_user.id,
            last_modified_by_id=current_user.id,
            category_id=category.id if category else None,
            icon_name=final_icon,
            quantity_value=item_quantity_value,
            quantity_unit_id=item_quantity_unit_id,
            quantity_display_text=item_quantity_display_text,
            translations=translations if translations else {},
        )

        session.add(item)
        await session.commit()
        await session.refresh(item)

        return item


class SharingService:
    """Service for handling shopping list sharing operations."""

    @staticmethod
    async def notify_list_shared(
        list_id: int,
        list_data: dict,
        new_member_email: str,
        current_user_id: str,
        inviter_email: str,
    ):
        """Send notifications when a list is shared."""
        # WebSocket notification
        try:
            await websocket_service.notify_list_shared(
                list_id=list_id,
                list_data=list_data,
                new_member_email=new_member_email,
                user_id=current_user_id,
            )
        except Exception as e:
            logger.exception("Failed to send WebSocket list_shared notification")
        
        # Email notification
        try:
            await send_list_invitation_email(
                to_email=new_member_email,
                list_data=list_data,
                inviter_email=inviter_email,
            )
        except Exception as e:
            logger.exception("Failed to send list invitation email")

    @staticmethod
    async def notify_member_removed(
        list_id: int,
        removed_user_id: str,
        current_user_id: str,
    ):
        """Send notification when a member is removed from a list."""
        try:
            await websocket_service.notify_member_removed(
                list_id=list_id,
                removed_user_id=removed_user_id,
                user_id=current_user_id,
            )
        except Exception as e:
            logger.exception("Failed to send WebSocket member_removed notification")

    @staticmethod
    async def send_invitation_email(to_email: str, list_data: dict, inviter_email: str):
        """Send invitation email for list sharing."""
        try:
            await send_list_invitation_email(
                to_email=to_email,
                list_data=list_data,
                inviter_email=inviter_email,
            )
        except Exception as e:
            logger.exception(f"Failed to send list invitation email to {to_email}")
    """Service for sharing shopping lists."""
    
    @staticmethod
    async def share_list_with_user(
        shopping_list: ShoppingList,
        user_email: str,
        current_user: User,
        session: AsyncSession
    ) -> ShoppingList:
        """Share a shopping list with a user by email."""
        # Find the user to share with
        result = await session.execute(select(User).where(User.email == user_email))
        user_to_share_with = result.scalars().first()

        if not user_to_share_with:
            # User doesn't exist - send invitation email
            await SharingService._send_invitation_to_nonexistent_user(
                shopping_list, user_email, current_user
            )
            return shopping_list

        # User exists - proceed with sharing
        if user_to_share_with not in shopping_list.shared_with:
            shopping_list.shared_with.append(user_to_share_with)
            await session.commit()
            await session.refresh(shopping_list, attribute_names=["shared_with", "owner"])

        # Send notifications
        await SharingService._send_sharing_notifications(
            shopping_list, user_email, current_user
        )

        return shopping_list

    @staticmethod
    async def _send_invitation_to_nonexistent_user(
        shopping_list: ShoppingList,
        user_email: str,
        current_user: User
    ):
        """Send invitation email to non-existent user."""
        list_data = {
            "id": shopping_list.id,
            "name": shopping_list.name,
            "description": shopping_list.description,
            "owner_id": str(shopping_list.owner_id),
            "created_at": shopping_list.created_at.isoformat(),
            "updated_at": shopping_list.updated_at.isoformat(),
            "members": [],
        }

        try:
            await send_list_invitation_email(
                to_email=user_email,
                list_data=list_data,
                inviter_email=current_user.email,
            )
            logger.info(f"Invitation email sent successfully to {user_email}")
        except Exception:
            logger.exception(f"Failed to send invitation email to {user_email}")
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send invitation email. Please try again.",
            )

    @staticmethod
    async def _send_sharing_notifications(
        shopping_list: ShoppingList,
        user_email: str,
        current_user: User
    ):
        """Send WebSocket and email notifications for sharing."""
        list_data = {
            "id": shopping_list.id,
            "name": shopping_list.name,
            "description": shopping_list.description,
            "owner_id": str(shopping_list.owner_id),
            "created_at": shopping_list.created_at.isoformat(),
            "updated_at": shopping_list.updated_at.isoformat(),
            "members": [
                {"email": u.email, "id": str(u.id)} for u in shopping_list.shared_with
            ],
        }

        # WebSocket notification
        try:
            await websocket_service.notify_list_shared(
                list_id=shopping_list.id,
                list_data=list_data,
                new_member_email=user_email,
                user_id=str(current_user.id),
            )
        except Exception:
            logger.exception("Failed to send WebSocket list_shared notification")

        # Email notification
        try:
            await send_list_invitation_email(
                to_email=user_email,
                list_data=list_data,
                inviter_email=current_user.email,
            )
        except Exception:
            logger.exception("Failed to send invitation email")