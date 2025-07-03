#!/usr/bin/env python3
"""
Test script for AI Provider Integration

This script tests the AI provider functionality without requiring
a full database setup. It's useful for validating the provider pattern
and configuration.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.core.config import settings
from app.services.ai_factory import AIProviderFactory, get_ai_provider


async def test_provider_info():
    """Test getting provider information."""
    print("=== AI Provider Information ===")
    try:
        info = AIProviderFactory.get_provider_info()
        print(f"Provider: {info['provider_name']}")
        print(f"Model: {info['model_name']}")
        print(f"Status: {info['status']}")
        if 'error' in info:
            print(f"Error: {info['error']}")
        return info['status'] == 'active'
    except Exception as e:
        print(f"Error getting provider info: {e}")
        return False


async def test_text_generation():
    """Test basic text generation."""
    print("\n=== Text Generation Test ===")
    try:
        provider = get_ai_provider()
        prompt = "Categorize this item: milk. Return only the category name."
        result = await provider.generate_text(prompt)
        print(f"Prompt: {prompt}")
        print(f"Response: {result}")
        return True
    except Exception as e:
        print(f"Error in text generation: {e}")
        return False


async def test_category_suggestion():
    """Test category suggestion (without database)."""
    print("\n=== Category Suggestion Test ===")
    try:
        provider = get_ai_provider()
        category_names = ["Dairy", "Produce", "Meat", "Pantry", "Beverages"]
        result = await provider.suggest_category_async("milk", category_names)
        print(f"Item: milk")
        print(f"Available categories: {category_names}")
        print(f"Suggested category: {result}")
        return True
    except Exception as e:
        print(f"Error in category suggestion: {e}")
        return False


async def test_icon_suggestion():
    """Test icon suggestion."""
    print("\n=== Icon Suggestion Test ===")
    try:
        provider = get_ai_provider()
        result = await provider.suggest_icon("milk", "Dairy")
        print(f"Item: milk, Category: Dairy")
        print(f"Suggested icon: {result}")
        return True
    except Exception as e:
        print(f"Error in icon suggestion: {e}")
        return False


async def test_name_standardization():
    """Test item name standardization and translation."""
    print("\n=== Name Standardization Test ===")
    try:
        provider = get_ai_provider()
        result = await provider.standardize_and_translate_item_name("mléko")
        print(f"Original: mléko")
        print(f"Standardized: {result.get('standardized_name', 'N/A')}")
        print(f"Translations: {result.get('translations', {})}")
        return True
    except Exception as e:
        print(f"Error in name standardization: {e}")
        return False


def print_configuration():
    """Print current configuration."""
    print("=== Configuration ===")
    print(f"AI_PROVIDER: {settings.AI_PROVIDER}")
    
    if settings.AI_PROVIDER.lower() == "gemini":
        print(f"GEMINI_MODEL_NAME: {settings.GEMINI_MODEL_NAME}")
        print(f"GOOGLE_API_KEY: {'Set' if settings.GOOGLE_API_KEY else 'Not Set'}")
    elif settings.AI_PROVIDER.lower() == "ollama":
        print(f"OLLAMA_BASE_URL: {settings.OLLAMA_BASE_URL}")
        print(f"OLLAMA_MODEL_NAME: {settings.OLLAMA_MODEL_NAME}")
        print(f"OLLAMA_TIMEOUT: {settings.OLLAMA_TIMEOUT}")


async def main():
    """Run all tests."""
    print("AI Provider Integration Test")
    print("=" * 40)
    
    print_configuration()
    print()
    
    tests = [
        ("Provider Info", test_provider_info),
        ("Text Generation", test_text_generation),
        ("Category Suggestion", test_category_suggestion),
        ("Icon Suggestion", test_icon_suggestion),
        ("Name Standardization", test_name_standardization),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            success = await test_func()
            results[test_name] = success
        except Exception as e:
            print(f"Test {test_name} failed with exception: {e}")
            results[test_name] = False
    
    print("\n=== Test Results ===")
    for test_name, success in results.items():
        status = "PASS" if success else "FAIL"
        print(f"{test_name}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    print(f"\nPassed: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("All tests passed! AI provider integration is working correctly.")
        return 0
    else:
        print("Some tests failed. Check configuration and provider setup.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
