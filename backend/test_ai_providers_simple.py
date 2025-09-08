#!/usr/bin/env python3
"""
Simple AI Provider Test Script

This script tests both Gemini and Ollama providers individually to verify
they are working correctly and measure their basic performance.
"""

import asyncio
import time
import sys
import os

# Add the backend app directory to Python path
sys.path.append("/home/honzik/GitHub/FamilyCart/FamilyCart/backend")

from app.core.config import settings
from app.services.ai_factory import AIProviderFactory
from app.services.gemini_provider import GeminiProvider
from app.services.ollama_provider import OllamaProvider


async def test_provider(provider, provider_name, test_items):
    """Test a specific provider with basic operations."""
    print(f"\n🧪 Testing {provider_name} Provider")
    print("=" * 50)

    for item in test_items:
        print(f"\n📝 Testing with item: '{item}'")

        # Test categorization
        start_time = time.time()
        try:
            category = await provider.suggest_category_async(item, [])
            categorization_time = time.time() - start_time
            print(f"  ✅ Categorization: {category} ({categorization_time:.3f}s)")
        except Exception as e:
            categorization_time = time.time() - start_time
            print(f"  ❌ Categorization failed: {e} ({categorization_time:.3f}s)")

        # Test icon suggestion
        start_time = time.time()
        try:
            icon = await provider.suggest_icon(item, "Produce")
            icon_time = time.time() - start_time
            print(f"  ✅ Icon suggestion: {icon} ({icon_time:.3f}s)")
        except Exception as e:
            icon_time = time.time() - start_time
            print(f"  ❌ Icon suggestion failed: {e} ({icon_time:.3f}s)")

        # Test text generation
        start_time = time.time()
        try:
            prompt = f"Describe '{item}' in one sentence."
            text = await provider.generate_text(prompt)
            text_time = time.time() - start_time
            print(f"  ✅ Text generation: {text[:50]}... ({text_time:.3f}s)")
        except Exception as e:
            text_time = time.time() - start_time
            print(f"  ❌ Text generation failed: {e} ({text_time:.3f}s)")


async def main():
    """Main test function."""
    print("🔬 AI Provider Individual Testing")
    print("=" * 50)

    # Test items for basic functionality
    test_items = ["organic apples", "whole milk", "chicken breast"]

    # Test Gemini Provider directly
    if settings.GOOGLE_API_KEY:
        print(f"\n🧠 Direct Gemini Provider Test")
        print(f"   API Key: {settings.GOOGLE_API_KEY[:20]}...")
        print(f"   Model: {settings.GEMINI_MODEL_NAME}")

        try:
            gemini_provider = GeminiProvider()
            await test_provider(gemini_provider, "Gemini", test_items)
        except Exception as e:
            print(f"❌ Failed to initialize Gemini provider: {e}")
    else:
        print("⚠️  Skipping Gemini test (no API key)")

    # Test Ollama Provider directly
    print(f"\n🦙 Direct Ollama Provider Test")
    print(f"   Base URL: {settings.OLLAMA_BASE_URL}")
    print(f"   Model: {settings.OLLAMA_MODEL_NAME}")

    try:
        ollama_provider = OllamaProvider()
        await test_provider(ollama_provider, "Ollama", test_items)
    except Exception as e:
        print(f"❌ Failed to initialize Ollama provider: {e}")

    # Test factory switching
    print(f"\n🏭 Testing Provider Factory Switching")
    print("=" * 50)

    # Test Gemini via factory
    if settings.GOOGLE_API_KEY:
        print(f"\n🔄 Testing Gemini via Factory")
        original_provider = settings.AI_PROVIDER
        try:
            settings.AI_PROVIDER = "gemini"
            AIProviderFactory.reset_provider()
            factory_gemini = AIProviderFactory.get_provider()
            print(f"   Provider: {factory_gemini.provider_name}")
            print(f"   Model: {factory_gemini.model_name}")

            # Quick test
            result = await factory_gemini.suggest_category_async("test item", [])
            print(f"   ✅ Quick test result: {result}")
        except Exception as e:
            print(f"   ❌ Factory Gemini test failed: {e}")
        finally:
            settings.AI_PROVIDER = original_provider

    # Test Ollama via factory
    print(f"\n🔄 Testing Ollama via Factory")
    original_provider = settings.AI_PROVIDER
    try:
        settings.AI_PROVIDER = "ollama"
        AIProviderFactory.reset_provider()
        factory_ollama = AIProviderFactory.get_provider()
        print(f"   Provider: {factory_ollama.provider_name}")
        print(f"   Model: {factory_ollama.model_name}")

        # Quick test
        result = await factory_ollama.suggest_category_async("test item", [])
        print(f"   ✅ Quick test result: {result}")
    except Exception as e:
        print(f"   ❌ Factory Ollama test failed: {e}")
    finally:
        settings.AI_PROVIDER = original_provider
        AIProviderFactory.reset_provider()


if __name__ == "__main__":
    asyncio.run(main())
