"""
Fallback AI Service Module for FamilyCart

This module provides a fallback AI service that automatically switches to Ollama
when Gemini rate limits are reached, ensuring continuous AI functionality.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.services.ai_factory import get_ai_provider
from app.services.gemini_provider import GeminiProvider
from app.services.ollama_provider import OllamaProvider
from app.core.cache import cache_service

# Configure logging
logger = logging.getLogger(__name__)


class FallbackAIService:
    """
    AI service with automatic fallback to Ollama when Gemini rate limits are reached.

    This service attempts to use the configured primary provider (usually Gemini)
    and falls back to Ollama if rate limits or other errors occur.
    """

    def __init__(self):
        """Initialize the fallback AI service."""
        self._primary_provider = None
        self._fallback_provider = None
        self._rate_limit_detected = False
        self._rate_limit_reset_time = None

    @property
    def primary_provider(self):
        """Get the primary AI provider instance (lazy initialization)."""
        if self._primary_provider is None:
            try:
                self._primary_provider = get_ai_provider()
            except Exception as e:
                logger.error(f"Failed to initialize primary provider: {e}")
                self._primary_provider = None
        return self._primary_provider

    @property
    def fallback_provider(self):
        """Get the fallback AI provider instance (lazy initialization)."""
        if self._fallback_provider is None:
            try:
                # Always use Ollama as fallback
                self._fallback_provider = OllamaProvider()
                logger.info("Fallback Ollama provider initialized")
            except Exception as e:
                logger.error(f"Failed to initialize fallback provider: {e}")
                self._fallback_provider = None
        return self._fallback_provider

    def _is_rate_limit_error(self, error: Exception) -> bool:
        """
        Check if the error indicates a rate limit has been reached.

        Args:
            error: The exception to check

        Returns:
            bool: True if this is a rate limit error
        """
        error_str = str(error).lower()
        rate_limit_indicators = [
            "rate limit",
            "quota exceeded",
            "too many requests",
            "429",
            "resource exhausted",
            "rate_limit_exceeded",
        ]
        return any(indicator in error_str for indicator in rate_limit_indicators)

    async def _try_with_fallback(
        self, operation_name: str, primary_func, fallback_func
    ):
        """
        Try an operation with the primary provider, fallback to Ollama if needed.

        Args:
            operation_name: Name of the operation for logging
            primary_func: Async function to call on primary provider
            fallback_func: Async function to call on fallback provider

        Returns:
            Result from either primary or fallback provider
        """
        # If we recently detected a rate limit and it hasn't reset, go straight to fallback
        if self._rate_limit_detected and self._rate_limit_reset_time:
            import time

            if time.time() < self._rate_limit_reset_time:
                logger.info(
                    f"Rate limit still active, using fallback for {operation_name}"
                )
                if self.fallback_provider:
                    return await fallback_func()
                else:
                    raise Exception(
                        "Both primary and fallback providers are unavailable"
                    )

        # Try primary provider first
        if self.primary_provider:
            try:
                logger.debug(f"Attempting {operation_name} with primary provider")
                result = await primary_func()

                # Reset rate limit flag on successful operation
                if self._rate_limit_detected:
                    self._rate_limit_detected = False
                    self._rate_limit_reset_time = None
                    logger.info("Rate limit appears to have been reset")

                return result

            except Exception as e:
                logger.warning(f"Primary provider failed for {operation_name}: {e}")

                # Check if this is a rate limit error
                if self._is_rate_limit_error(e):
                    self._rate_limit_detected = True
                    # Set reset time to 1 hour from now
                    import time

                    self._rate_limit_reset_time = time.time() + 3600
                    logger.error(
                        f"Rate limit detected for primary provider, switching to fallback"
                    )

                    # Cache the rate limit status
                    await cache_service.set(
                        "gemini_rate_limit_detected", "true", expire=3600
                    )

                # Try fallback provider
                if self.fallback_provider:
                    try:
                        logger.info(
                            f"Attempting {operation_name} with fallback provider"
                        )
                        result = await fallback_func()
                        logger.info(f"Fallback provider succeeded for {operation_name}")
                        return result
                    except Exception as fallback_error:
                        logger.error(
                            f"Fallback provider also failed for {operation_name}: {fallback_error}"
                        )
                        raise fallback_error
                else:
                    raise e
        else:
            # No primary provider, try fallback
            if self.fallback_provider:
                logger.info(
                    f"No primary provider available, using fallback for {operation_name}"
                )
                return await fallback_func()
            else:
                raise Exception("No AI providers available")

    async def generate_text(self, prompt: str) -> str:
        """
        Generate text using primary provider with fallback to Ollama.

        Args:
            prompt (str): The prompt to send to the model.

        Returns:
            str: The generated text.
        """

        async def primary_func():
            return await self.primary_provider.generate_text(prompt)

        async def fallback_func():
            return await self.fallback_provider.generate_text(prompt)

        return await self._try_with_fallback(
            "text generation", primary_func, fallback_func
        )

    async def suggest_category(self, item_name: str, db: AsyncSession) -> str:
        """
        Suggest a category for a given item name with fallback support.

        Args:
            item_name (str): The name of the item.
            db (AsyncSession): The async database session.

        Returns:
            str: The suggested category name.
        """

        async def primary_func():
            return await self.primary_provider.suggest_category(item_name, db)

        async def fallback_func():
            return await self.fallback_provider.suggest_category(item_name, db)

        return await self._try_with_fallback(
            "category suggestion", primary_func, fallback_func
        )

    async def suggest_category_async(
        self, item_name: str, category_names: List[str]
    ) -> str:
        """
        Suggest a category for a given item name (async version) with fallback support.

        Args:
            item_name (str): The name of the item.
            category_names (List[str]): List of existing category names.

        Returns:
            str: The suggested category name.
        """

        async def primary_func():
            return await self.primary_provider.suggest_category_async(
                item_name, category_names
            )

        async def fallback_func():
            return await self.fallback_provider.suggest_category_async(
                item_name, category_names
            )

        return await self._try_with_fallback(
            "category suggestion async", primary_func, fallback_func
        )

    async def suggest_icon(self, item_name: str, category_name: str) -> str:
        """
        Suggest a Material Design icon for a given item name and category with fallback support.

        Args:
            item_name (str): The name of the item.
            category_name (str): The category of the item.

        Returns:
            str: The suggested icon name.
        """

        async def primary_func():
            return await self.primary_provider.suggest_icon(item_name, category_name)

        async def fallback_func():
            return await self.fallback_provider.suggest_icon(item_name, category_name)

        return await self._try_with_fallback(
            "icon suggestion", primary_func, fallback_func
        )

    async def standardize_and_translate_item_name(
        self, item_name: str
    ) -> Dict[str, Any]:
        """
        Standardize an item name and provide translations with fallback support.

        Args:
            item_name (str): The name of the item.

        Returns:
            Dict[str, Any]: A dictionary containing the standardized name and translations.
        """

        async def primary_func():
            return await self.primary_provider.standardize_and_translate_item_name(
                item_name
            )

        async def fallback_func():
            return await self.fallback_provider.standardize_and_translate_item_name(
                item_name
            )

        return await self._try_with_fallback(
            "standardization and translation", primary_func, fallback_func
        )

    def get_provider_info(self) -> dict:
        """
        Get information about the current AI provider and fallback status.

        Returns:
            dict: Information about the current provider and fallback status.
        """
        info = {
            "rate_limit_detected": self._rate_limit_detected,
            "fallback_available": self.fallback_provider is not None,
        }

        if self._rate_limit_detected and self.fallback_provider:
            info.update(
                {
                    "provider_name": self.fallback_provider.provider_name,
                    "model_name": self.fallback_provider.model_name,
                    "status": "fallback_active",
                }
            )
        elif self.primary_provider:
            info.update(
                {
                    "provider_name": self.primary_provider.provider_name,
                    "model_name": self.primary_provider.model_name,
                    "status": "primary_active",
                }
            )
        else:
            info.update(
                {"provider_name": "none", "model_name": "none", "status": "error"}
            )

        return info


# Global instance for backward compatibility
fallback_ai_service = FallbackAIService()
