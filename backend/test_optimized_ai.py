#!/usr/bin/env python3
"""
Test optimized AI service with gemini-1.5-flash
This should dramatically improve performance from 5-10s to <1s
"""
import asyncio
import time
import sys
import random

# Add backend to path
sys.path.insert(0, "/home/honzik/GitHub/FamilyCart/FamilyCart/backend")

import google.generativeai as genai
from app.core.config import settings
from app.core.cache import cache_service


class OptimizedAIService:
    """
    Optimized AI service using gemini-1.5-flash for better performance
    """

    def __init__(self):
        if not settings.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is not set")

        genai.configure(api_key=settings.GOOGLE_API_KEY)
        # Use the faster model
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        print(f"✅ Initialized Optimized AI Service with gemini-1.5-flash")

    async def suggest_category_optimized(
        self, item_name: str, category_names: list[str]
    ) -> str:
        """
        Optimized category suggestion with faster model and simpler prompt
        """
        cache_key = f"category_suggestion:{item_name.lower().strip()}"
        cached_category = await cache_service.get(cache_key)
        if cached_category:
            print(
                f"💨 Cache hit for category suggestion: {item_name} -> {cached_category}"
            )
            return cached_category

        # Simplified prompt optimized for gemini-1.5-flash
        prompt = f"""Categorize this shopping item: {item_name}

Categories: {', '.join(category_names)}

Return only the category name."""

        try:
            start_time = time.time()
            response = await self.model.generate_content_async(prompt)
            end_time = time.time()

            suggested_category = response.text.strip().replace(".", "").title()
            duration = end_time - start_time

            print(
                f"⚡ AI call completed in {duration:.3f}s: {item_name} -> {suggested_category}"
            )

            # Cache for 6 months
            await cache_service.set(
                cache_key, suggested_category, expire=3600 * 24 * 180
            )
            return suggested_category

        except Exception as e:
            print(f"❌ Error in optimized category suggestion: {e}")
            return "Uncategorized"

    async def suggest_icon_optimized(self, item_name: str, category_name: str) -> str:
        """
        Optimized icon suggestion
        """
        cache_key = f"icon_suggestion:{item_name.lower().strip()}:{category_name.lower().strip()}"
        cached_icon = await cache_service.get(cache_key)
        if cached_icon:
            print(
                f"💨 Cache hit for icon suggestion: {item_name}/{category_name} -> {cached_icon}"
            )
            return cached_icon

        # Simplified prompt for icon suggestion
        prompt = f"""Suggest a Material Design icon for: {item_name} (category: {category_name})

Common icons: shopping_cart, local_grocery_store, fastfood, local_cafe, hardware, lightbulb, spa, pets, leaf

Return only the icon name."""

        try:
            start_time = time.time()
            response = await self.model.generate_content_async(prompt)
            end_time = time.time()

            suggested_icon = response.text.strip().replace(".", "")
            duration = end_time - start_time

            print(
                f"⚡ Icon AI call completed in {duration:.3f}s: {item_name} -> {suggested_icon}"
            )

            # Fallback to default if not in common list
            if not suggested_icon or len(suggested_icon) > 30:
                suggested_icon = "shopping_cart"

            await cache_service.set(cache_key, suggested_icon, expire=3600 * 24 * 180)
            return suggested_icon

        except Exception as e:
            print(f"❌ Error in optimized icon suggestion: {e}")
            return "shopping_cart"


async def test_optimized_performance():
    """
    Test the optimized AI service performance
    """
    print("🚀 Testing Optimized AI Service Performance")
    print("==========================================")

    # Setup cache
    await cache_service.setup()
    print(f"✅ Cache service setup complete")

    # Initialize optimized service
    optimized_service = OptimizedAIService()

    # Test items (mix of cached and uncached)
    test_items = [
        "jablko",  # Czech for apple
        "mléko",  # Czech for milk (might be cached)
        f"unique_test_{random.randint(10000, 99999)}",  # Definitely uncached
        "bread",  # Common English item
        "šampon",  # Czech item (might be cached)
    ]

    category_names = [
        "Produce",
        "Dairy",
        "Meat",
        "Pantry",
        "Frozen",
        "Beverages",
        "Snacks",
        "Personal Care",
        "Household",
        "Uncategorized",
    ]

    print(f"\n📊 Performance Test Results:")
    print(
        f"{'Item':<20} {'Cache':<8} {'Category Time':<15} {'Icon Time':<12} {'Total Time':<12} {'Category':<12}"
    )
    print("-" * 85)

    total_time = 0

    for item in test_items:
        overall_start = time.time()

        # Test category suggestion
        cat_start = time.time()
        category = await optimized_service.suggest_category_optimized(
            item, category_names
        )
        cat_time = time.time() - cat_start

        # Test icon suggestion
        icon_start = time.time()
        icon = await optimized_service.suggest_icon_optimized(item, category)
        icon_time = time.time() - icon_start

        overall_time = time.time() - overall_start
        total_time += overall_time

        # Determine if it was cached
        cache_status = "HIT" if cat_time < 0.1 else "MISS"

        print(
            f"{item:<20} {cache_status:<8} {cat_time:<15.3f} {icon_time:<12.3f} {overall_time:<12.3f} {category:<12}"
        )

    avg_time = total_time / len(test_items)
    print("-" * 85)
    print(f"📈 Average time per item: {avg_time:.3f}s")
    print(f"📈 Total time for {len(test_items)} items: {total_time:.3f}s")

    print(f"\n🎯 Expected Improvements:")
    print(f"   Previous performance (uncached): 5-10s per item")
    print(f"   Optimized performance (uncached): <1s per item")
    print(f"   Cached performance: <0.1s per item")
    print(f"   Overall improvement: 5-10x faster!")


if __name__ == "__main__":
    asyncio.run(test_optimized_performance())
