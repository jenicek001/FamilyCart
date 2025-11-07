"""
AI Service Module for FamilyCart

This module provides a unified interface for AI operations using the provider pattern.
It supports multiple AI providers (Gemini, Ollama) and delegates operations to the
configured provider with automatic fallback support.
"""

import logging
from typing import Any, Dict, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.services.fallback_ai_service import fallback_ai_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIService:
    """
    Unified AI service that delegates operations to the configured AI provider.

    This service acts as a facade for different AI providers, ensuring backward
    compatibility while supporting multiple AI backends with automatic fallback.
    """

    def __init__(self):
        """
        Initialize the AI service.
        Uses the fallback service for automatic provider switching.
        """
        self._fallback_service = fallback_ai_service

    @property
    def provider(self):
        """Get the AI provider instance (for backward compatibility)."""
        return self._fallback_service.primary_provider

    async def generate_text(self, prompt: str) -> str:
        """
        Generate text using the configured AI provider with automatic fallback.

        Args:
            prompt (str): The prompt to send to the model.

        Returns:
            str: The generated text.
        """
        return await self._fallback_service.generate_text(prompt)

    async def suggest_category(self, item_name: str, db: AsyncSession) -> str:
        """
        Suggest a category for a given item name using the configured AI provider with automatic fallback.

        Args:
            item_name (str): The name of the item.
            db (AsyncSession): The async database session.

        Returns:
            str: The suggested category name.
        """
        return await self._fallback_service.suggest_category(item_name, db)

    async def suggest_category_async(
        self, item_name: str, category_names: List[str]
    ) -> str:
        """
        Suggest a category for a given item name (async version) with automatic fallback.

        Args:
            item_name (str): The name of the item.
            category_names (List[str]): List of existing category names.

        Returns:
            str: The suggested category name.
        """
        return await self._fallback_service.suggest_category_async(
            item_name, category_names
        )

    async def suggest_icon(self, item_name: str, category_name: str) -> str:
        """
        Suggest a Material Design icon for a given item name and category with automatic fallback.

        Args:
            item_name (str): The name of the item.
            category_name (str): The category of the item.

        Returns:
            str: The suggested icon name.
        """
        return await self._fallback_service.suggest_icon(item_name, category_name)

    async def standardize_and_translate_item_name(
        self, item_name: str
    ) -> Dict[str, Any]:
        """
        Standardize an item name and provide translations with automatic fallback.

        Args:
            item_name (str): The name of the item.

        Returns:
            Dict[str, Any]: A dictionary containing the standardized name and translations.
        """
        return await self._fallback_service.standardize_and_translate_item_name(
            item_name
        )

    def get_provider_info(self) -> dict:
        """
        Get information about the current AI provider and fallback status.

        Returns:
            dict: Information about the current provider and fallback status.
        """
        return self._fallback_service.get_provider_info()


# Global instance for backward compatibility
ai_service = AIService()
