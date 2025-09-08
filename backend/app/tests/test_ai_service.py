import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch

from sqlalchemy.orm import Session

from app.services.ai_service import AIService
from app.core.cache import CacheService
from app.models.category import Category
from app.crud.crud_category import CRUDCategory

# Using pytest-asyncio for async tests
pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_db_session():
    """Fixture for a mocked SQLAlchemy Session."""
    return MagicMock(spec=Session)


@pytest.fixture
def ai_service_mocker():
    """
    This fixture automatically patches all external dependencies for ai_service
    for every test in this module.
    """
    with patch(
        "google.generativeai.GenerativeModel", new_callable=MagicMock
    ) as mock_genai_model, patch(
        "app.services.ai_service.cache_service", spec=CacheService
    ) as mock_cache_service, patch(
        "app.services.ai_service.crud_category", spec=CRUDCategory
    ) as mock_crud_category:

        # Configure default mock behaviors
        mock_genai_model.return_value.generate_content_async = AsyncMock()
        mock_cache_service.get = AsyncMock(return_value=None)
        mock_cache_service.set = AsyncMock()
        mock_crud_category.get_multi.return_value = [
            Category(id=1, name="Fruits", icon_name="apple"),
            Category(id=2, name="Bakery", icon_name="bread-slice"),
        ]

        # Yield a dictionary of mocks for tests to use for configuration
        yield {
            "model": mock_genai_model.return_value,
            "cache": mock_cache_service,
            "crud_category": mock_crud_category,
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
    Test suggest_category for an item not in cache.
    It should call the AI model and cache the result.
    """
    item_name = "Baguette"
    cache_key = f"category_suggestion:{item_name.lower().strip()}"
    ai_service.mocks["cache"].get.return_value = None

    # Mock the AI's response
    ai_response_text = "Bakery"
    mock_response = MagicMock()
    mock_response.text = ai_response_text
    ai_service.mocks["model"].generate_content_async.return_value = mock_response

    suggested_category = await ai_service.suggest_category(item_name, mock_db_session)

    # Assertions
    ai_service.mocks["crud_category"].get_multi.assert_called_once_with(
        mock_db_session, limit=1000
    )
    ai_service.mocks["model"].generate_content_async.assert_called_once()
    ai_service.mocks["cache"].get.assert_called_once_with(cache_key)
    ai_service.mocks["cache"].set.assert_called_once_with(
        cache_key, "Bakery", expire=3600 * 24 * 180
    )
    assert suggested_category == "Bakery"


async def test_suggest_category_cached_item(
    ai_service: AIService, mock_db_session: MagicMock
):
    """
    Test suggest_category for an item that is already in the cache.
    It should return the cached value without calling the AI model.
    """
    item_name = "Croissant"
    cached_category = "Bakery"
    cache_key = f"category_suggestion:{item_name.lower().strip()}"
    ai_service.mocks["cache"].get.return_value = cached_category

    suggested_category = await ai_service.suggest_category(item_name, mock_db_session)

    # Assertions
    ai_service.mocks["cache"].get.assert_called_once_with(cache_key)
    ai_service.mocks["model"].generate_content_async.assert_not_called()
    ai_service.mocks["cache"].set.assert_not_called()
    assert suggested_category == cached_category


async def test_suggest_icon_new_item(ai_service: AIService):
    """
    Test suggest_icon for a new item not in cache.
    It should call the AI model and cache the result.
    """
    item_name = "Blueberry"
    category_name = "Fruits"
    cache_key = (
        f"icon_suggestion:{item_name.lower().strip()}:{category_name.lower().strip()}"
    )
    ai_service.mocks["cache"].get.return_value = None

    # Mock the AI's response
    ai_response_text = "leaf"  # The model should return just the icon name
    mock_response = MagicMock()
    mock_response.text = ai_response_text
    ai_service.mocks["model"].generate_content_async.return_value = mock_response

    suggested_icon = await ai_service.suggest_icon(item_name, category_name)

    # Assertions
    ai_service.mocks["model"].generate_content_async.assert_called_once()
    ai_service.mocks["cache"].get.assert_called_once_with(cache_key)
    ai_service.mocks["cache"].set.assert_called_once_with(
        cache_key, "leaf", expire=3600 * 24 * 180
    )
    assert suggested_icon == "leaf"


async def test_suggest_icon_cached_item(ai_service: AIService):
    """
    Test suggest_icon for an item that is already in the cache.
    It should return the cached value without calling the AI model.
    """
    item_name = "Strawberry"
    category_name = "Fruits"
    cached_icon = "park"  # Using a valid icon from the list
    cache_key = (
        f"icon_suggestion:{item_name.lower().strip()}:{category_name.lower().strip()}"
    )
    ai_service.mocks["cache"].get.return_value = cached_icon

    suggested_icon = await ai_service.suggest_icon(item_name, category_name)

    # Assertions
    ai_service.mocks["cache"].get.assert_called_once_with(cache_key)
    ai_service.mocks["model"].generate_content_async.assert_not_called()
    ai_service.mocks["cache"].set.assert_not_called()
    assert suggested_icon == cached_icon


async def test_standardize_and_translate_item_name_new_item(ai_service: AIService):
    """
    Test standardize_and_translate_item_name for a new item.
    It should call the AI model, parse the response, and cache the result.
    """
    item_name = "huevos"
    cache_key = f"standardized_name:{item_name.lower().strip()}"
    ai_service.mocks["cache"].get.return_value = None

    # Mock the AI's response
    response_data = {
        "standardized_name": "Eggs",
        "translations": {"es": "Huevos", "fr": "Oeufs", "de": "Eier"},
    }
    # The model now returns a clean JSON string, so we mock that
    ai_response_text = json.dumps(response_data)
    mock_response = MagicMock()
    mock_response.text = ai_response_text
    ai_service.mocks["model"].generate_content_async.return_value = mock_response

    result = await ai_service.standardize_and_translate_item_name(item_name)

    # Assertions
    ai_service.mocks["model"].generate_content_async.assert_called_once()
    ai_service.mocks["cache"].get.assert_called_once_with(cache_key)
    ai_service.mocks["cache"].set.assert_called_once_with(
        cache_key, json.dumps(response_data), expire=3600 * 24 * 180
    )
    assert result == response_data


async def test_standardize_and_translate_item_name_cached_item(ai_service: AIService):
    """
    Test standardize_and_translate_item_name for a cached item.
    It should return the parsed cached value without calling the AI model.
    """
    item_name = "leche"
    cached_data = {
        "standardized_name": "Milk",
        "translations": {"es": "Leche", "fr": "Lait", "de": "Milch"},
    }
    cached_json_string = json.dumps(cached_data)
    cache_key = f"standardized_name:{item_name.lower().strip()}"
    ai_service.mocks["cache"].get.return_value = cached_json_string

    result = await ai_service.standardize_and_translate_item_name(item_name)

    # Assertions
    ai_service.mocks["cache"].get.assert_called_once_with(cache_key)
    ai_service.mocks["model"].generate_content_async.assert_not_called()
    ai_service.mocks["cache"].set.assert_not_called()
    assert result == cached_data
