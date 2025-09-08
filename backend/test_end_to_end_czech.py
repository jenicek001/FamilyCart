#!/usr/bin/env python3
"""
End-to-end test for Czech item categorization.
Tests the full flow: user registration -> login -> shopping list creation -> Czech item addition -> categorization verification
"""

import asyncio
import requests
import json
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

# Test data
TEST_USER = {
    "email": "czech_test@example.com",
    "password": "TestPassword123!",
    "nickname": "Czech Tester",
}

CZECH_ITEMS = [
    {"name": "mléko", "expected_category": "Dairy", "description": "fresh milk"},
    {
        "name": "rohlíky",
        "expected_category": "Pantry",
        "description": "fresh bread rolls",
    },  # Pantry is correct for bread
    {
        "name": "jablka",
        "expected_category": "Produce",
        "description": "red apples",
    },  # Produce is correct for fruits
    {"name": "sýr", "expected_category": "Dairy", "description": "cheese"},
    {"name": "kuřecí maso", "expected_category": "Meat", "description": "chicken meat"},
]


class EndToEndTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        self.shopping_list_id = None

    def log(self, message: str):
        print(f"[E2E TEST] {message}")

    def register_user(self) -> bool:
        """Register a new test user"""
        self.log("Registering test user...")

        response = self.session.post(f"{API_V1}/auth/register", json=TEST_USER)

        if response.status_code == 201:
            user_data = response.json()
            self.user_id = user_data.get("id")
            self.log(f"User registered successfully: {user_data.get('email')}")
            return True
        elif (
            response.status_code == 400
            and "REGISTER_USER_ALREADY_EXISTS" in response.text
        ):
            self.log("User already exists, continuing...")
            return True
        else:
            self.log(f"Registration failed: {response.status_code} - {response.text}")
            return False

    def login_user(self) -> bool:
        """Login the test user"""
        self.log("Logging in user...")

        response = self.session.post(
            f"{API_V1}/auth/jwt/login",
            data={"username": TEST_USER["email"], "password": TEST_USER["password"]},
        )

        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data["access_token"]
            self.session.headers.update(
                {"Authorization": f"Bearer {self.access_token}"}
            )
            self.log("Login successful")
            return True
        else:
            self.log(f"Login failed: {response.status_code} - {response.text}")
            return False

    def get_user_info(self) -> bool:
        """Get current user info to verify authentication"""
        self.log("Getting user info...")

        response = self.session.get(f"{API_V1}/users/me")

        if response.status_code == 200:
            user_data = response.json()
            self.user_id = user_data["id"]
            self.log(f"User info retrieved: {user_data.get('email')}")
            return True
        else:
            self.log(
                f"Failed to get user info: {response.status_code} - {response.text}"
            )
            return False

    def create_shopping_list(self) -> bool:
        """Create a test shopping list"""
        self.log("Creating shopping list...")

        response = self.session.post(
            f"{API_V1}/shopping-lists/",
            json={
                "name": "Czech Items Test List",
                "description": "Testing Czech item categorization",
            },
        )

        if response.status_code == 200:
            list_data = response.json()
            self.shopping_list_id = list_data["id"]
            self.log(f"Shopping list created: {list_data['name']}")
            return True
        else:
            self.log(
                f"Failed to create shopping list: {response.status_code} - {response.text}"
            )
            return False

    def add_czech_item(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a Czech item to the shopping list"""
        self.log(f"Adding Czech item: {item_data['name']}")

        response = self.session.post(
            f"{API_V1}/shopping-lists/{self.shopping_list_id}/items/",
            json={
                "name": item_data["name"],
                "description": item_data.get("description", ""),
                "quantity": "1",
            },
        )

        if response.status_code == 200:
            item = response.json()
            self.log(f"Item added successfully: {item['name']}")
            self.log(f"Full item data: {json.dumps(item, indent=2, default=str)}")
            self.log(f"  - Category: {item.get('category', {}).get('name', 'None')}")
            self.log(f"  - Standardized name: {item.get('standardized_name', 'None')}")
            self.log(f"  - Icon: {item.get('icon_name', 'None')}")
            return item
        else:
            self.log(f"Failed to add item: {response.status_code} - {response.text}")
            return {}

    def verify_categorization(
        self, item: Dict[str, Any], expected_category: str
    ) -> bool:
        """Verify that the item was categorized correctly"""
        if not item:
            self.log(f"❌ No item data to verify")
            return False

        category_data = item.get("category")
        if category_data is None:
            actual_category = "None"
        else:
            actual_category = category_data.get("name", "None")

        if actual_category == expected_category:
            self.log(f"✅ Categorization correct: {item['name']} -> {actual_category}")
            return True
        else:
            self.log(
                f"❌ Categorization incorrect: {item['name']} -> {actual_category} (expected: {expected_category})"
            )
            return False

    def cleanup(self):
        """Clean up test data"""
        if self.shopping_list_id:
            self.log("Cleaning up shopping list...")
            response = self.session.delete(
                f"{API_V1}/shopping-lists/{self.shopping_list_id}"
            )
            if response.status_code == 200:
                self.log("Shopping list deleted successfully")
            else:
                self.log(f"Failed to delete shopping list: {response.status_code}")

    async def run_test(self) -> bool:
        """Run the complete end-to-end test"""
        self.log("Starting end-to-end Czech categorization test")

        try:
            # Setup phase
            if not self.register_user():
                return False

            if not self.login_user():
                return False

            if not self.get_user_info():
                return False

            if not self.create_shopping_list():
                return False

            # Test phase
            correct_categorizations = 0
            total_items = len(CZECH_ITEMS)

            for item_data in CZECH_ITEMS:
                item = self.add_czech_item(item_data)
                if item and self.verify_categorization(
                    item, item_data["expected_category"]
                ):
                    correct_categorizations += 1

                # Wait a bit between requests to avoid rate limiting
                await asyncio.sleep(1)

            # Results
            accuracy = (correct_categorizations / total_items) * 100
            self.log(f"\n=== TEST RESULTS ===")
            self.log(f"Total items tested: {total_items}")
            self.log(f"Correctly categorized: {correct_categorizations}")
            self.log(f"Accuracy: {accuracy:.1f}%")

            success = accuracy >= 80.0  # Accept 80% accuracy as success
            if success:
                self.log("✅ END-TO-END TEST PASSED")
            else:
                self.log("❌ END-TO-END TEST FAILED")

            return success

        except Exception as e:
            self.log(f"Test failed with exception: {e}")
            return False
        finally:
            self.cleanup()


async def main():
    """Main test function"""
    tester = EndToEndTester()
    success = await tester.run_test()

    if not success:
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
