import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from app.core.cache import CacheService
from app.crud.crud_category import CRUDCategory
from app.models.category import Category
from app.services.ai_service import AIService

# Using pytest-asyncio for async tests
pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_db_session():
    """Fixture for a mocked SQLAlchemy Session."""
    return MagicMock(spec=Session)


@pytest.fixture
def ai_service_mocker():
    """
    This fixture automatically patches the fallback_ai_service for ai_service tests.
    The new AI service delegates to fallback_ai_service, so we mock that instead.
    """
    with (
        patch("app.services.ai_service.fallback_ai_service") as mock_fallback_service,
    ):
        # Configure default mock behaviors
        mock_fallback_service.suggest_category = AsyncMock(return_value="Fruits")
        mock_fallback_service.suggest_category_async = AsyncMock(return_value="Fruits")
        mock_fallback_service.suggest_icon = AsyncMock(return_value="apple")
        mock_fallback_service.standardize_and_translate_item_name = AsyncMock(
            return_value={
                "standardized_name": "Apple",
                "translations": {"cs": "Jablko", "de": "Apfel"},
            }
        )
        mock_fallback_service.generate_text = AsyncMock(return_value="Generated text")
        mock_fallback_service.get_provider_info = MagicMock(
            return_value={"primary": "gemini", "fallback_available": True}
        )

        # Yield the mock for tests to configure
        yield {
            "fallback_service": mock_fallback_service,
        }


@pytest.fixture
def ai_service(ai_service_mocker):
    """
    Fixture to get a fresh instance of AIService for each test.
    Relies on ai_service_mocker to have patched dependencies.
    """
    # Reset the singleton instance to ensure test isolation
    if hasattr(AIService, "_instance"):
        delattr(AIService, "_instance")

    service = AIService()
    # Attach mocks to the service instance for easy access in tests
    service.mocks = ai_service_mocker
    return service


async def test_suggest_category_new_item(
    ai_service: AIService, mock_db_session: MagicMock
):
    """
    Test suggest_category delegates to fallback_ai_service.
    """
    item_name = "Baguette"

    # The mock is already configured to return "Fruits"
    suggested_category = await ai_service.suggest_category(item_name, mock_db_session)

    # Assertions - verify it called the fallback service
    ai_service.mocks["fallback_service"].suggest_category.assert_called_once_with(
        item_name, mock_db_session
    )
    assert suggested_category == "Fruits"


async def test_suggest_category_cached_item(
    ai_service: AIService, mock_db_session: MagicMock
):
    """
    Test suggest_category for a cached item (handled by fallback service).
    """
    item_name = "Croissant"
    # Reconfigure the mock to return a different value
    ai_service.mocks["fallback_service"].suggest_category.return_value = "Bakery"

    suggested_category = await ai_service.suggest_category(item_name, mock_db_session)

    # Assertions
    ai_service.mocks["fallback_service"].suggest_category.assert_called_once_with(
        item_name, mock_db_session
    )
    assert suggested_category == "Bakery"


async def test_suggest_icon_new_item(ai_service: AIService):
    """
    Test suggest_icon delegates to fallback_ai_service.
    """
    item_name = "Blueberry"
    category_name = "Fruits"

    # Reconfigure for this specific test
    ai_service.mocks["fallback_service"].suggest_icon.return_value = "leaf"

    suggested_icon = await ai_service.suggest_icon(item_name, category_name)

    # Assertions
    ai_service.mocks["fallback_service"].suggest_icon.assert_called_once_with(
        item_name, category_name
    )
    assert suggested_icon == "leaf"


async def test_suggest_icon_cached_item(ai_service: AIService):
    """
    Test suggest_icon for a cached item (handled by fallback service).
    """
    item_name = "Strawberry"
    category_name = "Fruits"

    # Reconfigure mock
    ai_service.mocks["fallback_service"].suggest_icon.return_value = "park"

    suggested_icon = await ai_service.suggest_icon(item_name, category_name)

    # Assertions
    ai_service.mocks["fallback_service"].suggest_icon.assert_called_once_with(
        item_name, category_name
    )
    assert suggested_icon == "park"


async def test_standardize_and_translate_item_name_new_item(ai_service: AIService):
    """
    Test standardize_and_translate_item_name delegates to fallback service.
    """
    item_name = "huevos"

    # The mock is already configured with a default return value
    result = await ai_service.standardize_and_translate_item_name(item_name)

    # Assertions
    ai_service.mocks[
        "fallback_service"
    ].standardize_and_translate_item_name.assert_called_once_with(item_name)
    assert "standardized_name" in result
    assert "translations" in result


async def test_standardize_and_translate_item_name_cached_item(ai_service: AIService):
    """
    Test standardize_and_translate_item_name for a cached item (handled by fallback service).
    """
    item_name = "pomme"

    # Reconfigure mock for cached scenario
    cached_data = {
        "standardized_name": "Apple",
        "translations": {"fr": "Pomme", "es": "Manzana"},
    }
    ai_service.mocks[
        "fallback_service"
    ].standardize_and_translate_item_name.return_value = cached_data

    result = await ai_service.standardize_and_translate_item_name(item_name)

    # Assertions
    ai_service.mocks[
        "fallback_service"
    ].standardize_and_translate_item_name.assert_called_once_with(item_name)
    assert result == cached_data
