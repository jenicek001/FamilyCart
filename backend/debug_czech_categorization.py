#!/usr/bin/env python3
"""
Debug script to test Czech language item categorization.
"""
import os
import sys
import asyncio
import logging
from pathlib import Path

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add the backend directory to sys.path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "app"))


# Mock objects for testing - MUST BE DONE BEFORE IMPORTING AI SERVICE
class MockCategory:
    """Mock category for testing"""

    def __init__(self, name: str):
        self.name = name


class MockCRUDCategory:
    """Mock CRUD category for testing"""

    def get_multi(self, db, limit=100):
        """Mock the get_multi method that returns a list of categories"""
        return [
            MockCategory("Produce"),
            MockCategory("Dairy"),
            MockCategory("Meat"),
            MockCategory("Pantry"),
            MockCategory("Frozen"),
            MockCategory("Beverages"),
            MockCategory("Snacks"),
            MockCategory("Personal Care"),
            MockCategory("Household"),
        ]


# Patch the crud_category before importing ai_service
import sys

sys.modules["app.crud.crud_category"] = type(
    "MockModule", (), {"category": MockCRUDCategory()}
)()

import google.generativeai as genai
from app.core.config import settings
from app.services.ai_service import ai_service

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_czech_categorization():
    """Test categorization of Czech item names."""

    # Test items in Czech with expected categories
    test_items = [
        {"name": "mléko", "expected_category": "dairy", "english": "milk"},
        {"name": "rajčata", "expected_category": "produce", "english": "tomatoes"},
        {"name": "brambory", "expected_category": "produce", "english": "potatoes"},
        {"name": "sýr", "expected_category": "dairy", "english": "cheese"},
        {"name": "chleba", "expected_category": "pantry", "english": "bread"},
        {"name": "jahody", "expected_category": "produce", "english": "strawberries"},
        {"name": "zmrzlina", "expected_category": "frozen", "english": "ice cream"},
        {"name": "eidam", "expected_category": "dairy", "english": "edam cheese"},
        {
            "name": "maso na gril",
            "expected_category": "meat",
            "english": "grilling meat",
        },
    ]

    print("=== Testing Czech Item Categorization ===\n")

    # Test if Google API key is available
    if not settings.GOOGLE_API_KEY:
        print("❌ ERROR: GOOGLE_API_KEY not found in environment variables")
        print("Please set GOOGLE_API_KEY in your .env file")
        return

    print(f"✅ Google API Key found: {settings.GOOGLE_API_KEY[:10]}...")
    print(f"📋 Testing {len(test_items)} Czech items\n")

    # Create a simple mock database session - we just need an object to pass
    mock_db = object()  # The patched crud_category doesn't actually use this

    # Test each item
    results = []
    for item in test_items:
        try:
            print(f"🔍 Testing: '{item['name']}' ('{item['english']}')")

            # Get AI categorization
            suggested_category = await ai_service.suggest_category(
                item["name"], mock_db
            )

            # Check if it matches expected
            is_correct = suggested_category.lower() in [
                item["expected_category"].lower(),
                f"{item['expected_category']}s".lower(),  # plural version
                item["expected_category"].replace("_", " ").lower(),
            ]

            # Also check Czech categories
            czech_matches = {
                "mléčné výrobky": "dairy",
                "ovoce a zelenina": "produce",
                "groceries": "other",
            }

            if suggested_category.lower() in czech_matches:
                mapped_category = czech_matches[suggested_category.lower()]
                is_correct = mapped_category == item["expected_category"]

            status = "✅" if is_correct else "❌"
            print(
                f"   {status} Suggested: '{suggested_category}' | Expected: '{item['expected_category']}'"
            )

            results.append(
                {
                    "item": item["name"],
                    "english": item["english"],
                    "suggested": suggested_category,
                    "expected": item["expected_category"],
                    "correct": is_correct,
                }
            )

        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            results.append(
                {
                    "item": item["name"],
                    "english": item["english"],
                    "suggested": "ERROR",
                    "expected": item["expected_category"],
                    "correct": False,
                }
            )

        print()  # Empty line for readability

    # Summary
    correct_count = sum(1 for r in results if r["correct"])
    total_count = len(results)
    accuracy = (correct_count / total_count) * 100 if total_count > 0 else 0

    print("=== SUMMARY ===")
    print(f"📊 Accuracy: {correct_count}/{total_count} ({accuracy:.1f}%)")
    print()

    if correct_count < total_count:
        print("❌ Failed categorizations:")
        for result in results:
            if not result["correct"]:
                print(
                    f"   • {result['item']} ({result['english']}) -> '{result['suggested']}' (expected: '{result['expected']}')"
                )
        print()

    # Recommendations
    print("=== RECOMMENDATIONS ===")
    if accuracy < 70:
        print("🔧 ISSUES IDENTIFIED:")
        print("   1. AI prompt may not handle Czech language effectively")
        print("   2. Existing category list contains mixed languages")
        print("   3. Category matching logic needs improvement")
        print()
        print("💡 SUGGESTED FIXES:")
        print("   1. Update AI prompt to explicitly handle multiple languages")
        print("   2. Standardize category names to English in database")
        print("   3. Add language detection and translation to prompt")
        print("   4. Create better category mapping for multilingual support")
    else:
        print("✅ Categorization accuracy is acceptable")

    return results


async def test_translation_functionality():
    """Test the translation functionality specifically."""
    print("\n=== Testing Translation Functionality ===\n")

    czech_items = ["mléko", "rajčata", "sýr", "chleba"]

    for item_name in czech_items:
        try:
            print(f"🔍 Testing translation for: '{item_name}'")
            result = await ai_service.standardize_and_translate_item_name(item_name)

            print(f"   📝 Standardized: {result.get('standardized_name', 'N/A')}")
            if result.get("translations"):
                print(f"   🌍 Translations:")
                for lang, translation in result["translations"].items():
                    print(f"      {lang}: {translation}")
            print()

        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}\n")


async def main():
    """Main function to run all tests."""
    print("Czech Language Item Categorization Debug Tool")
    print("=" * 50)

    # Test categorization
    await test_czech_categorization()

    # Test translation
    await test_translation_functionality()

    print("=== Debug session complete ===")


if __name__ == "__main__":
    asyncio.run(main())
