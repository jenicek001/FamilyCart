#!/usr/bin/env python3
"""
Debug script to test the fallback logic directly.
"""

import asyncio
import logging
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, "/home/honzik/GitHub/FamilyCart/FamilyCart/backend")

from app.services.fallback_ai_service import fallback_ai_service

# Configure logging to see debug messages
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def test_fallback():
    """Test the fallback AI service directly."""

    print("Testing Fallback AI Service...")
    print("=" * 50)

    # Test if providers are initialized
    print(f"Primary provider: {fallback_ai_service.primary_provider}")
    print(f"Fallback provider: {fallback_ai_service.fallback_provider}")

    # Get provider info
    info = fallback_ai_service.get_provider_info()
    print(f"Provider info: {info}")

    print("\nTesting category suggestion with 'sůl do myčky'...")

    try:
        # This should trigger Gemini quota error and fallback to Ollama
        result = await fallback_ai_service.suggest_category_async(
            "sůl do myčky", ["Cleaning", "Food"]
        )
        print(f"Category suggestion result: {result}")

    except Exception as e:
        print(f"Error during category suggestion: {e}")

    print("\nTesting icon suggestion...")
    try:
        result = await fallback_ai_service.suggest_icon("sůl do myčky", "Cleaning")
        print(f"Icon suggestion result: {result}")
    except Exception as e:
        print(f"Error during icon suggestion: {e}")


if __name__ == "__main__":
    asyncio.run(test_fallback())
