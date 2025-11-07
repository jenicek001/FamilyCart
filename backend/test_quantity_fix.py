#!/usr/bin/env python3
"""
Test the quantity validation fix
"""
import os
import sys

sys.path.append("/home/honzik/GitHub/FamilyCart/FamilyCart/backend")

from app.schemas.item import ItemUpdate


def test_quantity_fix():
    """Test that quantity now accepts both strings and numbers"""
    print("🧪 Testing Quantity Validation Fix")
    print("=" * 40)

    test_cases = [
        {"quantity": "5", "expected": "5"},
        {"quantity": 5, "expected": "5"},
        {"quantity": 3.5, "expected": "3.5"},
        {"quantity": None, "expected": None},
        {"quantity": "2 lbs", "expected": "2 lbs"},
    ]

    all_passed = True

    for i, case in enumerate(test_cases):
        try:
            item_update = ItemUpdate(**{"quantity": case["quantity"]})
            result = item_update.quantity

            if result == case["expected"]:
                print(f"✅ Test {i+1}: {case['quantity']} -> '{result}' (correct)")
            else:
                print(
                    f"❌ Test {i+1}: {case['quantity']} -> '{result}' (expected '{case['expected']}')"
                )
                all_passed = False

        except Exception as e:
            print(f"❌ Test {i+1}: {case['quantity']} -> ERROR: {e}")
            all_passed = False

    print()
    if all_passed:
        print("🎉 All tests passed! The fix works correctly.")
    else:
        print("🚨 Some tests failed. There may still be issues.")

    return all_passed


if __name__ == "__main__":
    result = test_quantity_fix()
    sys.exit(0 if result else 1)
