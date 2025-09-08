#!/usr/bin/env python3
"""
Test Fallback AI Service

This script tests the fallback functionality by simulating rate limit scenarios
and verifying that the service automatically switches to Ollama.
"""

import asyncio
import sys
import os
import time

# Add the backend app directory to Python path
sys.path.append("/home/honzik/GitHub/FamilyCart/FamilyCart/backend")

from app.services.fallback_ai_service import FallbackAIService
from app.core.config import settings


async def test_fallback_functionality():
    """Test the fallback AI service functionality."""
    print("🔄 Testing Fallback AI Service")
    print("=" * 50)

    # Initialize the fallback service
    service = FallbackAIService()

    # Test provider info
    print("\n📊 Provider Information:")
    info = service.get_provider_info()
    for key, value in info.items():
        print(f"  {key}: {value}")

    # Test categorization with both providers
    test_items = ["apple", "milk", "bread"]

    print("\n🧪 Testing Categorization:")
    for item in test_items:
        try:
            start_time = time.time()
            category = await service.suggest_category_async(item, [])
            elapsed = time.time() - start_time
            print(f"  ✅ '{item}' -> '{category}' ({elapsed:.3f}s)")
        except Exception as e:
            print(f"  ❌ '{item}' -> Error: {e}")

    # Test manual rate limit detection
    print("\n⚠️  Testing Rate Limit Simulation:")

    # Simulate a rate limit error
    service._rate_limit_detected = True
    service._rate_limit_reset_time = time.time() + 10  # 10 seconds from now

    print("  Rate limit flag set, testing fallback...")

    try:
        start_time = time.time()
        category = await service.suggest_category_async("chicken", [])
        elapsed = time.time() - start_time
        print(f"  ✅ Fallback worked: 'chicken' -> '{category}' ({elapsed:.3f}s)")

        # Check provider info again
        info = service.get_provider_info()
        print(f"  📊 Current status: {info.get('status', 'unknown')}")
        print(f"  🔧 Current provider: {info.get('provider_name', 'unknown')}")

    except Exception as e:
        print(f"  ❌ Fallback failed: {e}")

    # Reset rate limit
    service._rate_limit_detected = False
    service._rate_limit_reset_time = None
    print("  🔄 Rate limit flag reset")

    # Test recovery
    print("\n🔄 Testing Recovery to Primary Provider:")
    try:
        start_time = time.time()
        category = await service.suggest_category_async("banana", [])
        elapsed = time.time() - start_time
        print(f"  ✅ Recovery worked: 'banana' -> '{category}' ({elapsed:.3f}s)")

        info = service.get_provider_info()
        print(f"  📊 Current status: {info.get('status', 'unknown')}")
        print(f"  🔧 Current provider: {info.get('provider_name', 'unknown')}")

    except Exception as e:
        print(f"  ❌ Recovery failed: {e}")


async def test_rate_limit_error_detection():
    """Test rate limit error detection logic."""
    print("\n🔍 Testing Rate Limit Error Detection:")

    service = FallbackAIService()

    # Test various error messages
    test_errors = [
        Exception("Rate limit exceeded"),
        Exception("Quota exceeded for this request"),
        Exception("Too many requests"),
        Exception("429 Client Error"),
        Exception("Resource exhausted"),
        Exception("rate_limit_exceeded"),
        Exception("Some other error"),
        Exception("Network timeout"),
    ]

    for i, error in enumerate(test_errors):
        is_rate_limit = service._is_rate_limit_error(error)
        status = "✅ DETECTED" if is_rate_limit else "❌ NOT DETECTED"
        print(f"  {i+1}. '{str(error)}' -> {status}")


if __name__ == "__main__":
    print("🚀 Starting Fallback AI Service Tests")

    asyncio.run(test_rate_limit_error_detection())

    print("\n" + "=" * 50)

    try:
        asyncio.run(test_fallback_functionality())
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()

    print("\n✅ Fallback AI Service Tests Completed")
