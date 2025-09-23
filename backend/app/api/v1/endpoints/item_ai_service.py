"""
AI-powered item processing service for shopping lists.
Handles categorization, standardization, and icon suggestions.
"""
import asyncio
import logging
from typing import Dict, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.services.ai_service import ai_service
from ..helpers import shopping_list_helpers as helpers

logger = logging.getLogger(__name__)


class ItemAIProcessor:
    """Service for AI-powered item processing."""

    @staticmethod
    async def process_item_with_ai(
        item_name: str,
        item_category_name: Optional[str],
        session: AsyncSession,
    ) -> Tuple[Optional[Category], Optional[str], Dict, Optional[str]]:
        """
        Process an item using AI to suggest category, standardize name, and suggest icon.
        
        Returns:
            Tuple of (category, standardized_name, translations, icon_name)
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
                    category = await helpers.get_or_create_category(category_name, session)

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
                        icon_name = "shopping_cart"  # Default fallback
                    except Exception as e:
                        logger.error(f"Icon suggestion failed: {e}")
                        icon_name = "shopping_cart"  # Default fallback

            except asyncio.TimeoutError:
                logger.warning(
                    f"AI processing timed out for item '{item_name}' - using fallbacks"
                )
                category_name = None
                standardized_name = None
                translations = {}

        except Exception as e:
            # Log the error but continue with item creation
            logger.error(f"Error during AI processing for item '{item_name}': {e}")

            # Fallback: use provided category if any
            if item_category_name:
                category = await helpers.get_or_create_category(item_category_name, session)

        return category, standardized_name, translations, icon_name