#!/usr/bin/env python3
"""
Test AI performance with proper cache setup
"""
import asyncio
import time
import sys
import random

# Add backend to path
sys.path.insert(0, "/home/honzik/GitHub/FamilyCart/FamilyCart/backend")

from app.services.ai_service import ai_service
from app.core.cache import cache_service


async def test_with_proper_cache_setup():
    print("=== Setting up cache service properly ===")

    # Ensure cache service is set up (this is normally done in main.py startup)
    await cache_service.setup()
    print(
        f"✅ Cache service setup complete. Client: {cache_service.redis_client is not None}"
    )

    # Test a simple cache operation
    await cache_service.set("test_setup", "working", expire=60)
    test_result = await cache_service.get("test_setup")
    print(f"✅ Cache test: {test_result}")

    # Now test AI service with cache working
    print("\n=== Testing AI with Working Cache ===")

    # Test with a common item that might benefit from caching
    test_item = "milk"

    print(f"🧪 First call for '{test_item}' (should be slow - cache miss)")
    start_time = time.time()

    category_names = ["Produce", "Dairy", "Pantry", "Meat", "Beverages", "Snacks"]
    category_name = await ai_service.suggest_category_async(test_item, category_names)

    first_call_time = time.time() - start_time
    print(f"  ✅ Category: '{category_name}' ({first_call_time:.2f}s)")

    # Second call - should be cached and fast
    print(f"\n🧪 Second call for '{test_item}' (should be fast - cache hit)")
    start_time = time.time()

    category_name_2 = await ai_service.suggest_category_async(test_item, category_names)

    second_call_time = time.time() - start_time
    print(f"  ✅ Category: '{category_name_2}' ({second_call_time:.2f}s)")

    # Compare results
    print(f"\n📊 Performance Comparison:")
    print(f"  First call (cache miss):  {first_call_time:.2f}s")
    print(f"  Second call (cache hit):  {second_call_time:.2f}s")
    print(
        f"  Improvement: {((first_call_time - second_call_time) / first_call_time * 100):.1f}%"
    )

    if second_call_time < 0.1:
        print("  ✅ EXCELLENT: Cache is working perfectly!")
    elif second_call_time < 1:
        print("  ✅ GOOD: Significant improvement from caching")
    else:
        print("  ⚠️  WARNING: Cache may not be working properly")


async def test_parallel_vs_sequential():
    """Test if we can make AI calls in parallel instead of sequential"""
    print("\n=== Testing Parallel vs Sequential AI Calls ===")

    test_item = f"test_parallel_item_{random.randint(10000, 99999)}"
    category_names = ["Produce", "Dairy", "Pantry", "Meat", "Beverages", "Snacks"]

    # Sequential (current approach)
    print("🧪 Sequential AI calls (current approach):")
    start_time = time.time()

    category_name = await ai_service.suggest_category_async(test_item, category_names)
    standardization_result = await ai_service.standardize_and_translate_item_name(
        test_item
    )
    icon_name = await ai_service.suggest_icon(test_item, category_name)

    sequential_time = time.time() - start_time
    print(f"  ✅ Sequential time: {sequential_time:.2f}s")

    # Parallel approach
    print("\n🧪 Parallel AI calls (optimized approach):")
    test_item_2 = f"test_parallel_item_{random.randint(10000, 99999)}"

    start_time = time.time()

    # Run all AI calls in parallel
    category_task = ai_service.suggest_category_async(test_item_2, category_names)
    translation_task = ai_service.standardize_and_translate_item_name(test_item_2)

    # Wait for category first (needed for icon)
    category_name_2 = await category_task

    # Now run icon suggestion in parallel with translation completion
    icon_task = ai_service.suggest_icon(test_item_2, category_name_2)

    # Wait for both to complete
    standardization_result_2, icon_name_2 = await asyncio.gather(
        translation_task, icon_task
    )

    parallel_time = time.time() - start_time
    print(f"  ✅ Parallel time: {parallel_time:.2f}s")

    print(f"\n📊 Parallel vs Sequential:")
    print(f"  Sequential: {sequential_time:.2f}s")
    print(f"  Parallel:   {parallel_time:.2f}s")
    print(
        f"  Improvement: {((sequential_time - parallel_time) / sequential_time * 100):.1f}%"
    )


if __name__ == "__main__":

    async def main():
        await test_with_proper_cache_setup()
        await test_parallel_vs_sequential()

        print("\n🎯 Next Steps:")
        print("1. Ensure cache service is properly initialized in production")
        print("2. Consider parallel AI calls to reduce total processing time")
        print("3. Add request timeouts to prevent extremely slow responses")

    asyncio.run(main())
