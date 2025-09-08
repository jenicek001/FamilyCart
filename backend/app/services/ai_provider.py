"""
Abstract AI Provider Interface for FamilyCart

This module defines the abstract base class for AI providers, ensuring
consistent interfaces across different AI service implementations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession


class AIProvider(ABC):
    """
    Abstract base class for AI providers.

    All AI providers must implement these methods to ensure consistent
    functionality across different AI services (Gemini, Ollama, etc.).
    """

    @abstractmethod
    async def generate_text(self, prompt: str) -> str:
        """
        Generate text using the AI model.

        Args:
            prompt (str): The prompt to send to the model.

        Returns:
            str: The generated text.
        """
        pass

    @abstractmethod
    async def suggest_category(self, item_name: str, db: AsyncSession) -> str:
        """
        Suggest a category for a given item name.

        Args:
            item_name (str): The name of the item.
            db (AsyncSession): The async database session.

        Returns:
            str: The suggested category name.
        """
        pass

    @abstractmethod
    async def suggest_category_async(
        self, item_name: str, category_names: List[str]
    ) -> str:
        """
        Suggest a category for a given item name (async version).

        Args:
            item_name (str): The name of the item.
            category_names (List[str]): List of existing category names.

        Returns:
            str: The suggested category name.
        """
        pass

    @abstractmethod
    async def suggest_icon(self, item_name: str, category_name: str) -> str:
        """
        Suggest a Material Design icon for a given item name and category.

        Args:
            item_name (str): The name of the item.
            category_name (str): The category of the item.

        Returns:
            str: The suggested icon name.
        """
        pass

    @abstractmethod
    async def standardize_and_translate_item_name(
        self, item_name: str
    ) -> Dict[str, Any]:
        """
        Standardize an item name and provide translations.

        Args:
            item_name (str): The name of the item.

        Returns:
            Dict[str, Any]: A dictionary containing the standardized name and translations.
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """
        Get the name of the AI provider.

        Returns:
            str: The provider name (e.g., "gemini", "ollama").
        """
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """
        Get the name of the AI model being used.

        Returns:
            str: The model name.
        """
        pass
