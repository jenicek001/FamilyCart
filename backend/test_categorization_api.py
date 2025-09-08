#!/usr/bin/env python3
"""
Test AI categorization API directly
"""
import requests
import json


def test_ai_categorization():
    """Test the AI categorization endpoint"""
    base_url = "http://localhost:8000/api/v1"

    # Test login
    print("🔐 Testing login...")
    login_data = {"username": "test@example.com", "password": "testpassword123"}

    response = requests.post(
        f"{base_url}/auth/jwt/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    if response.status_code == 200:
        token_data = response.json()
        token = token_data.get("access_token")
        print(f"✅ Login successful, token: {token[:20]}...")

        # Test categorization
        print("\n🤖 Testing AI categorization...")
        test_items = ["apple", "milk", "bread", "chicken breast", "detergent"]

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        for item in test_items:
            categorization_data = {"item_name": item}

            response = requests.post(
                f"{base_url}/ai/categorize-item",
                json=categorization_data,
                headers=headers,
            )

            if response.status_code == 200:
                result = response.json()
                category = result.get("category_name", "Unknown")
                print(f"  ✅ '{item}' -> '{category}'")
            else:
                print(f"  ❌ '{item}' -> Error {response.status_code}: {response.text}")

    else:
        print(f"❌ Login failed: {response.status_code} - {response.text}")


if __name__ == "__main__":
    test_ai_categorization()
