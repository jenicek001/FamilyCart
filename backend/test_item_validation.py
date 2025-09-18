#!/usr/bin/env python3
"""
Test script to debug the 422 Unprocessable Entity error when updating item quantity
"""
import asyncio
import os
import sys

sys.path.append("/home/honzik/GitHub/FamilyCart/FamilyCart/backend")

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.models.item import Item
from app.schemas.item import ItemUpdate


async def test_item_update_validation():
    """Test different ItemUpdate validation scenarios"""
    print("🧪 Testing ItemUpdate Schema Validation")
    print("=" * 50)

    # Test cases that might cause 422 errors
    test_cases = [
        {
            "name": "Valid quantity as string",
            "data": {"quantity": "5"},
            "should_pass": True,
        },
        {
            "name": "Valid quantity as integer",
            "data": {"quantity": 5},
            "should_pass": False,  # This might be the issue - expecting string but getting int
        },
        {
            "name": "Valid name update",
            "data": {"name": "Updated Apple"},
            "should_pass": True,
        },
        {
            "name": "Valid completion status",
            "data": {"is_completed": True},
            "should_pass": True,
        },
        {
            "name": "Mixed valid fields",
            "data": {"name": "New Item", "quantity": "3", "is_completed": False},
            "should_pass": True,
        },
        {"name": "Empty update", "data": {}, "should_pass": True},
        {
            "name": "Invalid category_id type",
            "data": {"category_id": "not_an_int"},
            "should_pass": False,
        },
        {
            "name": "Quantity as number instead of string",
            "data": {"quantity": 42},
            "should_pass": False,
        },
    ]

    results = []

    for test_case in test_cases:
        print(f"\n📝 Testing: {test_case['name']}")
        print(f"   Data: {test_case['data']}")

        try:
            # Try to create ItemUpdate object
            item_update = ItemUpdate(**test_case["data"])
            print(f"   ✅ Validation passed: {item_update.dict(exclude_unset=True)}")
            results.append(
                {
                    "test": test_case["name"],
                    "passed": True,
                    "expected": test_case["should_pass"],
                }
            )
        except ValidationError as e:
            print(f"   ❌ Validation failed: {e}")
            results.append(
                {
                    "test": test_case["name"],
                    "passed": False,
                    "expected": test_case["should_pass"],
                    "error": str(e),
                }
            )
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
            results.append(
                {
                    "test": test_case["name"],
                    "passed": False,
                    "expected": test_case["should_pass"],
                    "error": str(e),
                }
            )

    # Summary
    print("\n" + "=" * 50)
    print("📊 VALIDATION TEST RESULTS")
    print("=" * 50)

    failed_tests = []
    for result in results:
        status = "✅ PASS" if result["passed"] == result["expected"] else "❌ FAIL"
        print(f"{status} {result['test']}")
        if result["passed"] != result["expected"]:
            failed_tests.append(result)

    if failed_tests:
        print(f"\n🚨 Found {len(failed_tests)} unexpected results:")
        for test in failed_tests:
            print(
                f"   - {test['test']}: Expected {'pass' if test['expected'] else 'fail'}, got {'pass' if test['passed'] else 'fail'}"
            )
            if "error" in test:
                print(f"     Error: {test['error']}")
    else:
        print("\n🎉 All validation tests behaved as expected!")

    return len(failed_tests) == 0


async def main():
    print("🚀 Debugging Item Update 422 Errors")
    print("Testing Pydantic schema validation for ItemUpdate")
    print()

    success = await test_item_update_validation()

    print()
    if success:
        print("🎯 Schema validation tests passed. Issue might be elsewhere.")
    else:
        print("🚨 Found schema validation issues that could cause 422 errors.")

    return success


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
