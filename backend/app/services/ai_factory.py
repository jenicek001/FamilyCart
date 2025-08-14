"""
AI Provider Factory

This module provides a factory for creating the appropriate AI provider
based on the configuration settings.
"""

import logging
from typing import Optional

from app.core.config import settings
from app.services.ai_provider import AIProvider
from app.services.gemini_provider import GeminiProvider
from app.services.ollama_provider import OllamaProvider

logger = logging.getLogger(__name__)


class AIProviderFactory:
    """
    Factory class for creating AI providers based on configuration.
    """
    
    _instance: Optional[AIProvider] = None

    @classmethod
    def get_provider(cls) -> AIProvider:
        """
        Get the configured AI provider instance.
        
        Returns:
            AIProvider: The configured AI provider instance.
            
        Raises:
            ValueError: If an unsupported AI provider is configured.
        """
        if cls._instance is None:
            cls._instance = cls._create_provider()
        return cls._instance

    @classmethod
    def _create_provider(cls) -> AIProvider:
        """
        Create the AI provider based on configuration.
        
        Returns:
            AIProvider: The AI provider instance.
            
        Raises:
            ValueError: If an unsupported AI provider is configured.
        """
        provider_name = settings.AI_PROVIDER.lower()
        
        if provider_name == "gemini":
            logger.info("Initializing Gemini AI provider")
            return GeminiProvider()
        elif provider_name == "ollama":
            logger.info("Initializing Ollama AI provider")
            return OllamaProvider()
        else:
            supported_providers = ["gemini", "ollama"]
            raise ValueError(
                f"Unsupported AI provider: {settings.AI_PROVIDER}. "
                f"Supported providers: {', '.join(supported_providers)}"
            )

    @classmethod
    def reset_provider(cls):
        """
        Reset the provider instance (useful for testing or configuration changes).
        """
        cls._instance = None

    @classmethod
    def get_provider_info(cls) -> dict:
        """
        Get information about the current AI provider.
        
        Returns:
            dict: Information about the current provider.
        """
        try:
            provider = cls.get_provider()
            return {
                "provider_name": provider.provider_name,
                "model_name": provider.model_name,
                "status": "active"
            }
        except Exception as e:
            return {
                "provider_name": settings.AI_PROVIDER,
                "model_name": "unknown",
                "status": "error",
                "error": str(e)
            }


# Global instance for easy access
def get_ai_provider() -> AIProvider:
    """
    Get the AI provider instance.
    
    Returns:
        AIProvider: The configured AI provider.
    """
    return AIProviderFactory.get_provider()
