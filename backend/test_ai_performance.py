#!/usr/bin/env python3
"""
Test the performance of adding new items (cache misses)
This simulates the exact behavior when adding items via frontend
"""
import asyncio
import time
import sys
import random
import string

# Add backend to path
sys.path.insert(0, "/home/honzik/GitHub/FamilyCart/FamilyCart/backend")

from app.services.ai_service import ai_service


async def test_uncached_item_performance():
    """Test performance for adding completely new items (cache misses)"""

    # Generate unique item names to ensure cache misses
    test_items = [
        f"unique_test_item_{random.randint(10000, 99999)}_{chr(random.randint(97, 122))}"
        for _ in range(3)
    ]

    print("=== Testing AI Performance for New Items (Cache Misses) ===")
    print("This simulates adding items via frontend for the first time")
    print()

    for i, item_name in enumerate(test_items, 1):
        print(f"🧪 Test {i}/3: Processing item '{item_name}'")
        start_time = time.time()

        try:
            # Simulate the exact same sequence as the shopping list API
            print("  1. Getting category suggestion...")
            category_start = time.time()
            category_names = [
                "Produce",
                "Dairy",
                "Pantry",
                "Meat",
                "Beverages",
                "Snacks",
                "Frozen",
                "Personal Care",
            ]
            category_name = await ai_service.suggest_category_async(
                item_name, category_names
            )
            category_time = time.time() - category_start
            print(f"     ✅ Category: '{category_name}' ({category_time:.2f}s)")

            # 2. Get standardized name and translations
            print("  2. Getting name standardization...")
            translation_start = time.time()
            standardization_result = (
                await ai_service.standardize_and_translate_item_name(item_name)
            )
            translation_time = time.time() - translation_start
            standardized_name = standardization_result.get(
                "standardized_name", item_name
            )
            translations = standardization_result.get("translations", {})
            print(
                f"     ✅ Standardized: '{standardized_name}' ({translation_time:.2f}s)"
            )
            print(f"     📝 Translations: {translations}")

            # 3. Get icon suggestion
            print("  3. Getting icon suggestion...")
            icon_start = time.time()
            icon_name = await ai_service.suggest_icon(item_name, category_name)
            icon_time = time.time() - icon_start
            print(f"     ✅ Icon: '{icon_name}' ({icon_time:.2f}s)")

            total_time = time.time() - start_time
            print(f"  🏁 Total time: {total_time:.2f}s")
            print(
                f"     Breakdown: Category({category_time:.1f}s) + Translation({translation_time:.1f}s) + Icon({icon_time:.1f}s)"
            )

            # Analyze performance
            if total_time > 10:
                print(f"  ⚠️  SLOW: {total_time:.2f}s exceeds 10s threshold!")
            elif total_time > 5:
                print(f"  ⚠️  WARNING: {total_time:.2f}s is slower than expected")
            else:
                print(f"  ✅ GOOD: {total_time:.2f}s is acceptable")

        except Exception as e:
            print(f"  ❌ ERROR: {e}")

        print("-" * 60)

        # Small delay between tests
        if i < len(test_items):
            await asyncio.sleep(1)


async def test_cached_item_performance():
    """Test performance for items that should be cached"""

    common_items = ["milk", "bread", "eggs"]

    print("\n=== Testing AI Performance for Common Items (Potential Cache Hits) ===")

    for i, item_name in enumerate(common_items, 1):
        print(f"🧪 Cache Test {i}/3: Processing item '{item_name}'")
        start_time = time.time()

        try:
            # Same sequence as above
            category_names = [
                "Produce",
                "Dairy",
                "Pantry",
                "Meat",
                "Beverages",
                "Snacks",
                "Frozen",
                "Personal Care",
            ]
            category_name = await ai_service.suggest_category_async(
                item_name, category_names
            )
            standardization_result = (
                await ai_service.standardize_and_translate_item_name(item_name)
            )
            icon_name = await ai_service.suggest_icon(item_name, category_name)

            total_time = time.time() - start_time
            print(f"  🏁 Total time: {total_time:.2f}s")

            if total_time < 0.1:
                print(f"  ✅ CACHED: {total_time:.3f}s - excellent cache performance!")
            elif total_time < 1:
                print(f"  ✅ FAST: {total_time:.2f}s - likely cached or very fast AI")
            else:
                print(f"  📝 UNCACHED: {total_time:.2f}s - AI call was made")

        except Exception as e:
            print(f"  ❌ ERROR: {e}")

        print("-" * 40)


if __name__ == "__main__":

    async def main():
        print("🚀 Starting AI Performance Tests")
        print("=" * 60)

        # Test uncached items (the main concern)
        await test_uncached_item_performance()

        # Test potentially cached items for comparison
        await test_cached_item_performance()

        print("\n📊 Performance Test Complete!")
        print("If uncached items take >10s, we need to optimize the AI calls.")

    asyncio.run(main())
