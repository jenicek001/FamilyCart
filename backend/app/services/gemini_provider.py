"""
Gemini AI Provider Implementation

This module implements the AIProvider interface using Google's Gemini model
for AI-powered features in FamilyCart.
"""

import json
import logging
from typing import Any, Dict, List

import google.generativeai as genai
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.core.cache import cache_service
from app.core.config import settings
from app.models.category import Category
from app.services.ai_provider import AIProvider

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeminiProvider(AIProvider):
    """
    Google Gemini AI provider implementation.
    """

    def __init__(self):
        """
        Initialize the Gemini provider with API key and model configuration.
        """
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set in the environment variables.")

        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL_NAME)
            logger.info(
                f"Successfully initialized Gemini model: {settings.GEMINI_MODEL_NAME}"
            )
        except Exception as e:
            logger.error(f"Error configuring Google AI: {e}")
            raise

    @property
    def provider_name(self) -> str:
        """Get the provider name."""
        return "gemini"

    def _is_rate_limit_error(self, error: Exception) -> bool:
        """
        Check if the error indicates a rate limit or quota has been reached.

        Args:
            error: The exception to check

        Returns:
            bool: True if this is a rate limit error that should trigger fallback
        """
        error_str = str(error).lower()
        rate_limit_indicators = [
            "rate limit",
            "quota exceeded",
            "too many requests",
            "429",
            "resource exhausted",
            "rate_limit_exceeded",
            "current quota",
        ]
        return any(indicator in error_str for indicator in rate_limit_indicators)

    @property
    def model_name(self) -> str:
        """Get the model name."""
        return settings.GEMINI_MODEL_NAME

    async def generate_text(self, prompt: str) -> str:
        """
        Generate text using the Gemini model.

        Args:
            prompt (str): The prompt to send to the model.

        Returns:
            str: The generated text.
        """
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error generating text with Gemini: {e}")
            return "Error: Could not generate text."

    async def suggest_category(self, item_name: str, db: AsyncSession) -> str:
        """
        Suggest a category for a given item name using the Gemini model.

        Args:
            item_name (str): The name of the item.
            db (AsyncSession): The async database session.

        Returns:
            str: The suggested category name.
        """
        cache_key = f"category_suggestion:{item_name.lower().strip()}"
        cached_category = await cache_service.get(cache_key)
        if cached_category:
            logger.info(
                f"Cache hit for category suggestion: {item_name} -> {cached_category}"
            )
            return cached_category

        # Use async SQLAlchemy to get existing categories
        result = await db.execute(select(Category).limit(1000))
        existing_categories = result.scalars().all()
        category_names = [category.name for category in existing_categories]

        prompt = f"""
        Given the following list of existing shopping item categories:
        {', '.join(category_names)}

        What is the best category for the item "{item_name}"?
        
        IMPORTANT INSTRUCTIONS:
        - The item name might be in Czech, German, Spanish, French, or other languages
        - The category should be a single noun, in English, and singular
        - If a suitable category from the list exists, return it exactly as written
        - If not, suggest a new, appropriate category in English
        - Return ONLY the category name and nothing else - no punctuation, no explanations
        
        Examples:
        - For "mléko" (Czech for milk), return: Dairy
        - For "Granny Smith Apples", return: Produce  
        - For "Cheddar Cheese", return: Dairy
        - For "pain" (French for bread), return: Pantry
        
        Item to categorize: "{item_name}"
        """

        try:
            response = await self.model.generate_content_async(prompt)
            # First try to parse as JSON (legacy behavior)
            try:
                data = json.loads(response.text)
                suggested_category = (
                    data.get("category_name", "Uncategorized")
                    .strip()
                    .replace(".", "")
                    .title()
                )
            except (json.JSONDecodeError, KeyError):
                # Expected behavior: parse as plain text response
                suggested_category = response.text.strip().replace(".", "").title()
                logger.info(
                    f"Parsed plain text category response: {suggested_category}"
                )

            await cache_service.set(
                cache_key, suggested_category, expire=3600 * 24 * 180
            )  # Cache for 6 months
            return suggested_category
        except Exception as e:
            logger.error(f"Error suggesting category with Gemini: {e}")
            return "Uncategorized"

    async def suggest_category_async(
        self, item_name: str, category_names: List[str]
    ) -> str:
        """
        Suggest a category for a given item name using the Gemini model (async version).

        Args:
            item_name (str): The name of the item.
            category_names (List[str]): List of existing category names.

        Returns:
            str: The suggested category name.
        """
        cache_key = f"category_suggestion:{item_name.lower().strip()}"
        cached_category = await cache_service.get(cache_key)
        if cached_category:
            logger.info(
                f"Cache hit for category suggestion: {item_name} -> {cached_category}"
            )
            return cached_category

        prompt = f"""
        Given the following list of existing shopping item categories:
        {', '.join(category_names)}

        What is the best category for the item "{item_name}"?
        
        IMPORTANT INSTRUCTIONS:
        - The item name might be in Czech, German, Spanish, French, or other languages
        - The category should be a single noun, in English, and singular
        - If a suitable category from the list exists, return it exactly as written
        - If not, suggest a new, appropriate category in English
        - Return ONLY the category name and nothing else - no punctuation, no explanations
        
        Examples:
        - For "mléko" (Czech for milk), return: Dairy
        - For "Granny Smith Apples", return: Produce  
        - For "Cheddar Cheese", return: Dairy
        - For "pain" (French for bread), return: Pantry
        
        Item to categorize: "{item_name}"
        """

        try:
            response = await self.model.generate_content_async(prompt)
            # First try to parse as JSON (legacy behavior)
            try:
                data = json.loads(response.text)
                suggested_category = (
                    data.get("category_name", "Uncategorized")
                    .strip()
                    .replace(".", "")
                    .title()
                )
            except (json.JSONDecodeError, KeyError):
                # Expected behavior: parse as plain text response
                suggested_category = response.text.strip().replace(".", "").title()
                logger.info(
                    f"Parsed plain text category response: {suggested_category}"
                )

            await cache_service.set(
                cache_key, suggested_category, expire=3600 * 24 * 180
            )  # Cache for 6 months
            return suggested_category
        except Exception as e:
            logger.error(f"Error suggesting category with Gemini: {e}")
            # Re-raise rate limit and quota errors so fallback service can handle them
            if self._is_rate_limit_error(e):
                raise e
            return "Uncategorized"

    async def suggest_icon(self, item_name: str, category_name: str) -> str:
        """
        Suggest a Material Design icon for a given item name and category.

        Args:
            item_name (str): The name of the item.
            category_name (str): The category of the item.

        Returns:
            str: The suggested icon name.
        """
        cache_key = f"icon_suggestion:{item_name.lower().strip()}:{category_name.lower().strip()}"
        cached_icon = await cache_service.get(cache_key)
        if cached_icon:
            logger.info(
                f"Cache hit for icon suggestion: {item_name}/{category_name} -> {cached_icon}"
            )
            return cached_icon

        # A curated list of common icons. A more comprehensive list could be loaded from a file.
        icon_list = [
            "shopping_cart",
            "local_grocery_store",
            "fastfood",
            "local_bar",
            "local_cafe",
            "local_dining",
            "icecream",
            "local_pizza",
            "ramen_dining",
            "lunch_dining",
            "bakery_dining",
            "hardware",
            "home",
            "kitchen",
            "tv",
            "lightbulb",
            "chair",
            "bed",
            "camera",
            "movie",
            "music_note",
            "book",
            "school",
            "science",
            "pets",
            "park",
            "fitness_center",
            "checkroom",
            "face",
            "spa",
            "content_cut",
            "brush",
            "medical_services",
            "medication",
            "local_pharmacy",
            "local_hospital",
            "construction",
            "handyman",
            "plumbing",
            "electrical_services",
            "cleaning_services",
            "flight",
            "train",
            "directions_car",
            "local_taxi",
            "local_gas_station",
            "ev_station",
            "local_shipping",
            "local_post_office",
            "credit_card",
            "account_balance_wallet",
            "savings",
            "paid",
            "receipt_long",
            "work",
            "business_center",
            "computer",
            "phone_iphone",
            "smartphone",
            "tablet_mac",
            "watch",
            "devices",
            "toys",
            "sports_esports",
            "sports_soccer",
            "sports_basketball",
            "sports_tennis",
            "sports_volleyball",
            "sports_baseball",
            "sports_golf",
            "celebration",
            "cake",
            "card_giftcard",
            "redeem",
            "theaters",
            "attractions",
            "forest",
            "terrain",
            "ac_unit",
            "water_drop",
            "grass",
            "eco",
            "recycling",
            "compost",
            "pets",
            "leaf",
        ]

        prompt = f"""
        Given the item \"{item_name}\" in the category \"{category_name}\", what is the most appropriate Google Material Icon name from the following list?
        Icon List: {', '.join(icon_list)}

        Return only the icon name and nothing else.
        For example, for "Milk" in "Dairy", you should return "local_grocery_store".
        For "Laptop" in "Electronics", you should return "computer".
        For "Shampoo" in "Personal Care", you should return "spa".
        """

        try:
            response = await self.model.generate_content_async(prompt)
            # First try to parse as JSON (legacy behavior)
            try:
                data = json.loads(response.text)
                suggested_icon = (
                    data.get("icon_name", "shopping_cart").strip().replace(".", "")
                )
                logger.info(f"Parsed JSON icon response: {suggested_icon}")
            except (json.JSONDecodeError, KeyError):
                # Expected behavior: parse as plain text response
                suggested_icon = response.text.strip().replace(".", "")
                logger.info(f"Parsed plain text icon response: {suggested_icon}")

            if suggested_icon in icon_list:
                await cache_service.set(
                    cache_key, suggested_icon, expire=3600 * 24 * 180
                )  # Cache for 6 months
                return suggested_icon
            else:
                # Fallback to a generic icon if the suggested one is not in the list
                logger.warning(
                    f"Suggested icon '{suggested_icon}' not in the predefined list. Falling back to default."
                )
                await cache_service.set(
                    cache_key, "shopping_cart", expire=3600 * 24 * 180
                )  # Cache for 6 months
                return "shopping_cart"
        except Exception as e:
            logger.error(f"Error suggesting icon with Gemini: {e}")
            # Re-raise rate limit and quota errors so fallback service can handle them
            if self._is_rate_limit_error(e):
                raise e
            return "shopping_cart"

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
        cache_key = f"standardized_name:{item_name.lower().strip()}"
        cached_data = await cache_service.get(cache_key)
        if cached_data:
            logger.info(f"Cache hit for item standardization: {item_name}")
            return json.loads(cached_data)

        prompt = f"""
        Standardize the following shopping item name and provide translations in Spanish, French, and German.
        The original name might be a colloquialism, have typos, or be in a different language (including Czech, Slovak, Polish, or other languages).
        The standardized name should be the most common, generic English term for the item.
        
        Return the output as a JSON object with the following keys: "standardized_name", "translations".
        The "translations" value should be another JSON object with keys "es", "fr", "de".

        Examples:
        For "tommy toes":
        {{
            "standardized_name": "Tomatoes",
            "translations": {{
                "es": "Tomates",
                "fr": "Tomates", 
                "de": "Tomaten"
            }}
        }}

        For "mléko" (Czech):
        {{
            "standardized_name": "Milk",
            "translations": {{
                "es": "Leche",
                "fr": "Lait",
                "de": "Milch"
            }}
        }}

        For "dozen eggs":
        {{
            "standardized_name": "Eggs",
            "translations": {{
                "es": "Huevos",
                "fr": "Oeufs",
                "de": "Eier"
            }}
        }}

        Item name: "{item_name}"
        """

        try:
            response = await self.model.generate_content_async(prompt)
            # Clean the response text before parsing
            cleaned_response_text = response.text.strip()
            # Find the start and end of the JSON object
            start_index = cleaned_response_text.find("{")
            end_index = cleaned_response_text.rfind("}") + 1
            if start_index != -1 and end_index != 0:
                json_text = cleaned_response_text[start_index:end_index]
                data = json.loads(json_text)
                await cache_service.set(
                    cache_key, json.dumps(data), expire=3600 * 24 * 180
                )  # Cache for 6 months
                return data
            else:
                logger.error(
                    f"Could not find a valid JSON object in the response from Gemini."
                )
                return {"standardized_name": item_name, "translations": {}}
        except json.JSONDecodeError as e:
            logger.error(
                f"Error decoding JSON from Gemini: {e}\nResponse text: {response.text}"
            )
            return {"standardized_name": item_name, "translations": {}}
        except Exception as e:
            logger.error(
                f"Error standardizing and translating item name with Gemini: {e}"
            )
            # Re-raise rate limit and quota errors so fallback service can handle them
            if self._is_rate_limit_error(e):
                raise e
            return {"standardized_name": item_name, "translations": {}}
