#!/usr/bin/env python3
"""
Test the quantity update fix with a mock API call
"""
import asyncio
import os
import sys

sys.path.append("/home/honzik/GitHub/FamilyCart/FamilyCart/backend")

from app.schemas.item import ItemUpdate


async def test_api_request_format():
    """Test typical frontend API request formats"""
    print("🧪 Testing Frontend-style API Requests")
    print("=" * 45)

    # Simulate different ways the frontend might send quantity data
    test_requests = [
        {
            "name": "String quantity (should work)",
            "payload": {"quantity": "3"},
        },
        {
            "name": "Integer quantity (was failing, should now work)",
            "payload": {"quantity": 3},
        },
        {
            "name": "Float quantity (should work)",
            "payload": {"quantity": 2.5},
        },
        {
            "name": "Mixed update with number quantity",
            "payload": {"name": "Updated Item", "quantity": 5, "is_completed": False},
        },
        {
            "name": "Only name change (should work)",
            "payload": {"name": "New Name"},
        },
        {
            "name": "Only completion status (should work)",
            "payload": {"is_completed": True},
        },
    ]

    all_passed = True

    for test in test_requests:
        print(f"\n📝 Testing: {test['name']}")
        print(f"   Payload: {test['payload']}")

        try:
            # This simulates what FastAPI does when it receives the request
            item_update = ItemUpdate(**test["payload"])
            validated_data = item_update.model_dump(exclude_unset=True)
            print(f"   ✅ Success: {validated_data}")

            # Check that quantity was converted to string if it was a number
            if "quantity" in test["payload"] and "quantity" in validated_data:
                original = test["payload"]["quantity"]
                converted = validated_data["quantity"]
                expected = (
                    str(original) if isinstance(original, (int, float)) else original
                )

                if converted == expected:
                    print(
                        f"   🎯 Quantity conversion: {original} -> '{converted}' (correct)"
                    )
                else:
                    print(
                        f"   ❌ Quantity conversion failed: {original} -> '{converted}' (expected '{expected}')"
                    )
                    all_passed = False

        except Exception as e:
            print(f"   ❌ Validation failed: {e}")
            all_passed = False

    print("\n" + "=" * 45)
    if all_passed:
        print("🎉 All API request formats work! The 422 error should be fixed.")
    else:
        print("🚨 Some request formats still fail.")

    return all_passed


async def main():
    print("🚀 Testing Quantity Update Fix")
    print("Simulating frontend API requests to backend")
    print()

    success = await test_api_request_format()

    print()
    if success:
        print(
            "✅ Fix confirmed! Item quantity updates should now work from the frontend."
        )
    else:
        print("❌ Issues remain. May need additional fixes.")

    return success


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
