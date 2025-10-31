"""
Unit tests for AI Provider Factory and Providers

Tests the AI provider pattern         mock_settings.AI_PROVIDER = "gemini"
        mock_settings.GOOGLE_API_KEY = "test-key"
        mock_settings.GEMINI_MODEL_NAME = "gemini-2.5-flash-lite-preview-06-17"
        
        with patch('app.services.ai_factory.GeminiProvider') as mock_gemini:
            mock_instance = Mock()
            mock_instance.provider_name = "gemini"
            mock_instance.model_name = "gemini-2.5-flash-lite-preview-06-17"
            mock_gemini.return_value = mock_instance
            
            info = AIProviderFactory.get_provider_info()
            
            assert info == {
                "provider": "gemini",
                "model_name": "gemini-2.5-flash-lite-preview-06-17",including factory,
provider selection, and basic functionality of both Gemini and Ollama providers.
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.core.config import settings
from app.services.ai_factory import AIProviderFactory, get_ai_provider
from app.services.gemini_provider import GeminiProvider
from app.services.ollama_provider import OllamaProvider


class TestAIProviderFactory:
    """Tests for the AI Provider Factory."""

    def setup_method(self):
        """Reset factory state before each test."""
        AIProviderFactory.reset_provider()

    @patch("app.core.config.settings")
    @patch("app.services.gemini_provider.settings")
    def test_get_gemini_provider(self, mock_gemini_settings, mock_settings):
        """Test that factory returns Gemini provider when configured."""
        mock_settings.AI_PROVIDER = "gemini"
        mock_settings.GOOGLE_API_KEY = "test-key"
        mock_settings.GEMINI_MODEL_NAME = "gemini-2.5-flash-lite-preview-06-17"
        # Mock GEMINI_API_KEY to prevent validation error
        mock_gemini_settings.GEMINI_API_KEY = "test-key"

        with patch("app.services.ai_factory.GeminiProvider") as mock_gemini:
            mock_instance = Mock()
            mock_gemini.return_value = mock_instance

            provider = AIProviderFactory.get_provider()

            assert provider == mock_instance
            mock_gemini.assert_called_once()

    @patch("app.core.config.settings")
    @patch("app.services.gemini_provider.settings")
    def test_get_ollama_provider(self, mock_gemini_settings, mock_settings):
        """Test that factory returns Ollama provider when configured."""
        mock_settings.AI_PROVIDER = "ollama"
        mock_settings.OLLAMA_BASE_URL = "http://localhost:11434"
        mock_settings.OLLAMA_MODEL_NAME = "gemma3:4b"
        # Mock GEMINI_API_KEY to prevent validation error
        mock_gemini_settings.GEMINI_API_KEY = "test-key"

        with patch("app.services.ai_factory.OllamaProvider") as mock_ollama:
            mock_instance = Mock()
            mock_ollama.return_value = mock_instance

            provider = AIProviderFactory.get_provider()

            assert provider == mock_instance
            mock_ollama.assert_called_once()

    @patch("app.core.config.settings")
    @patch("app.services.gemini_provider.settings")
    def test_unsupported_provider_raises_error(self, mock_gemini_settings, mock_settings):
        """Test that unsupported provider raises ValueError."""
        mock_settings.AI_PROVIDER = "unsupported"
        # Mock GEMINI_API_KEY to prevent validation error
        mock_gemini_settings.GEMINI_API_KEY = "test-key"

        with pytest.raises(ValueError) as exc_info:
            AIProviderFactory.get_provider()

        assert "Unsupported AI provider: unsupported" in str(exc_info.value)

    @patch("app.core.config.settings")
    @patch("app.services.gemini_provider.settings")
    def test_provider_singleton_behavior(self, mock_gemini_settings, mock_settings):
        """Test that factory returns the same instance on multiple calls."""
        mock_settings.AI_PROVIDER = "gemini"
        mock_settings.GOOGLE_API_KEY = "test-key"
        mock_settings.GEMINI_MODEL_NAME = "gemini-2.5-flash-lite-preview-06-17"
        # Mock GEMINI_API_KEY to prevent validation error
        mock_gemini_settings.GEMINI_API_KEY = "test-key"

        with patch("app.services.ai_factory.GeminiProvider") as mock_gemini:
            mock_instance = Mock()
            mock_gemini.return_value = mock_instance

            provider1 = AIProviderFactory.get_provider()
            provider2 = AIProviderFactory.get_provider()

            assert provider1 is provider2
            mock_gemini.assert_called_once()  # Should only be called once

    @patch("app.core.config.settings")
    @patch("app.services.gemini_provider.settings")
    def test_provider_info_success(self, mock_gemini_settings, mock_settings):
        """Test getting provider info when provider is available."""
        mock_settings.AI_PROVIDER = "gemini"
        mock_settings.GOOGLE_API_KEY = "test-key"
        mock_settings.GEMINI_MODEL_NAME = "gemini-1.5-flash"
        # Mock GEMINI_API_KEY to prevent validation error
        mock_gemini_settings.GEMINI_API_KEY = "test-key"

        with patch("app.services.ai_factory.GeminiProvider") as mock_gemini:
            mock_instance = Mock()
            mock_instance.provider_name = "gemini"
            mock_instance.model_name = "gemini-1.5-flash"
            mock_gemini.return_value = mock_instance

            info = AIProviderFactory.get_provider_info()

            expected = {
                "provider_name": "gemini",
                "model_name": "gemini-1.5-flash",
                "status": "active",
            }
            assert info == expected

    @patch("app.core.config.settings")
    @patch("app.services.gemini_provider.settings")
    def test_provider_info_error(self, mock_gemini_settings, mock_settings):
        """Test getting provider info when provider fails to initialize."""
        mock_settings.AI_PROVIDER = "gemini"
        # Mock GEMINI_API_KEY as None to cause an error
        mock_gemini_settings.GEMINI_API_KEY = None

        info = AIProviderFactory.get_provider_info()

        assert info["status"] == "error"
        assert info["provider_name"] == "gemini"
        assert info["model_name"] == "unknown"
        assert "error" in info

    @patch("app.core.config.settings")
    @patch("app.services.gemini_provider.settings")
    def test_reset_provider(self, mock_gemini_settings, mock_settings):
        """Test that reset_provider clears the singleton instance."""
        mock_settings.AI_PROVIDER = "gemini"
        mock_settings.GOOGLE_API_KEY = "test-key"
        mock_settings.GEMINI_MODEL_NAME = "gemini-2.5-flash-lite-preview-06-17"
        # Mock GEMINI_API_KEY to prevent validation error
        mock_gemini_settings.GEMINI_API_KEY = "test-key"

        with patch("app.services.ai_factory.GeminiProvider") as mock_gemini:
            mock_instance = Mock()
            mock_gemini.return_value = mock_instance

            # Get provider to create instance
            provider1 = AIProviderFactory.get_provider()

            # Reset and get again
            AIProviderFactory.reset_provider()
            provider2 = AIProviderFactory.get_provider()

            # Should be different instances
            assert provider1 is not provider2
            assert mock_gemini.call_count == 2


class TestAIProviderIntegration:
    """Integration tests for AI providers."""

    def setup_method(self):
        """Reset factory state before each test."""
        AIProviderFactory.reset_provider()

    @patch("app.services.gemini_provider.settings")
    @patch("app.services.gemini_provider.genai")
    def test_gemini_provider_initialization(self, mock_genai, mock_settings):
        """Test Gemini provider initializes correctly."""
        mock_settings.GEMINI_API_KEY = "test-key"
        mock_settings.GEMINI_MODEL_NAME = "gemini-2.5-flash-lite-preview-06-17"

        mock_model = Mock()
        mock_genai.GenerativeModel.return_value = mock_model

        provider = GeminiProvider()

        assert provider.provider_name == "gemini"
        assert provider.model_name == "gemini-2.5-flash-lite-preview-06-17"
        mock_genai.configure.assert_called_once_with(api_key="test-key")
        mock_genai.GenerativeModel.assert_called_once_with(
            "gemini-2.5-flash-lite-preview-06-17"
        )

    @patch("app.services.gemini_provider.settings")
    def test_gemini_provider_missing_api_key(self, mock_settings):
        """Test Gemini provider raises error when API key is missing."""
        mock_settings.GEMINI_API_KEY = None

        with pytest.raises(ValueError) as exc_info:
            GeminiProvider()

        assert "GEMINI_API_KEY is not set" in str(exc_info.value)

    @patch("app.core.config.settings")
    @patch("app.services.ollama_provider.ollama")
    def test_ollama_provider_initialization(self, mock_ollama, mock_settings):
        """Test Ollama provider initializes correctly."""
        mock_settings.OLLAMA_BASE_URL = "http://localhost:11434"
        mock_settings.OLLAMA_MODEL_NAME = "gemma3:4b"

        mock_client = Mock()
        mock_ollama.AsyncClient.return_value = mock_client

        provider = OllamaProvider()

        assert provider.provider_name == "ollama"
        assert provider.model_name == "gemma3:4b"
        mock_ollama.AsyncClient.assert_called_once_with(host="http://localhost:11434")

    @patch("app.services.gemini_provider.settings")
    @patch("app.services.gemini_provider.genai")
    @patch("app.services.gemini_provider.cache_service")
    async def test_gemini_generate_text(self, mock_cache, mock_genai, mock_settings):
        """Test Gemini provider text generation."""
        mock_settings.GEMINI_API_KEY = "test-key"
        mock_settings.GEMINI_MODEL_NAME = "gemini-2.5-flash-lite-preview-06-17"

        # Setup mocks
        mock_model = AsyncMock()
        mock_response = Mock()
        mock_response.text = "Generated text"
        mock_model.generate_content_async.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        provider = GeminiProvider()
        result = await provider.generate_text("Test prompt")

        assert result == "Generated text"
        mock_model.generate_content_async.assert_called_once_with("Test prompt")

    @patch("app.core.config.settings")
    @patch("app.services.ollama_provider.ollama")
    async def test_ollama_generate_text(self, mock_ollama, mock_settings):
        """Test Ollama provider text generation."""
        mock_settings.OLLAMA_BASE_URL = "http://localhost:11434"
        mock_settings.OLLAMA_MODEL_NAME = "gemma3:4b"

        # Setup mocks
        mock_client = AsyncMock()
        mock_client.generate.return_value = {"response": "Generated text"}
        mock_ollama.AsyncClient.return_value = mock_client

        provider = OllamaProvider()
        result = await provider.generate_text("Test prompt")

        assert result == "Generated text"
        mock_client.generate.assert_called_once_with(
            model="gemma3:4b", prompt="Test prompt", options={"temperature": 0.7}
        )

    @patch("app.services.ai_factory.AIProviderFactory.get_provider")
    def test_get_ai_provider_function(self, mock_factory_get_provider):
        """Test the standalone get_ai_provider function."""
        mock_provider = Mock()
        mock_factory_get_provider.return_value = mock_provider

        provider = get_ai_provider()

        assert provider == mock_provider
        mock_factory_get_provider.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
