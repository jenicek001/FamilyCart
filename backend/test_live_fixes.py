#!/usr/bin/env python3
"""
Test script to verify the live fixes for AI fallback and UUID serialization.
This script will add items that trigger AI categorization and monitor for issues.
"""

import asyncio
import json
import logging
import time
from typing import Any, Dict

import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"


class LiveTester:
    def __init__(self):
        self.session = requests.Session()
        self.user_token = None
        self.shopping_list_id = None

    def authenticate(self) -> bool:
        """Authenticate with the API and get a token."""
        try:
            # Try to register a test user
            register_data = {
                "email": "test_fixes@example.com",
                "password": "testpassword123",
                "nickname": "TestUser",
                "first_name": "Test",
                "last_name": "User",
            }

            response = self.session.post(
                f"{API_BASE}/auth/register", json=register_data
            )
            if response.status_code == 201:
                logger.info("Test user registered successfully")
            elif response.status_code == 400 and "already registered" in response.text:
                logger.info("Test user already exists, proceeding with login")
            else:
                logger.error(
                    f"Registration failed: {response.status_code} - {response.text}"
                )

            # Login using form data (fastapi-users standard)
            login_data = {
                "username": "test_fixes@example.com",
                "password": "testpassword123",
            }

            login_response = self.session.post(
                f"{API_BASE}/auth/jwt/login", data=login_data
            )
            if login_response.status_code == 200:
                token_data = login_response.json()
                self.user_token = token_data["access_token"]
                self.session.headers.update(
                    {"Authorization": f"Bearer {self.user_token}"}
                )
                logger.info("Authentication successful")
                return True
            else:
                logger.error(
                    f"Login failed: {login_response.status_code} - {login_response.text}"
                )
                return False

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False

    def create_shopping_list(self) -> bool:
        """Create a test shopping list."""
        try:
            list_data = {
                "name": "AI Fallback Test List",
                "description": "Testing AI fallback and UUID serialization fixes",
            }

            response = self.session.post(f"{API_BASE}/shopping-lists/", json=list_data)
            if response.status_code in [200, 201]:
                list_info = response.json()
                self.shopping_list_id = list_info["id"]
                logger.info(f"Created shopping list: {self.shopping_list_id}")
                return True
            else:
                logger.error(
                    f"Failed to create shopping list: {response.status_code} - {response.text}"
                )
                return False

        except Exception as e:
            logger.error(f"Error creating shopping list: {e}")
            return False

    def add_item(self, name: str, quantity: str = "1 ks") -> Dict[str, Any]:
        """Add an item to the shopping list and return the response."""
        try:
            item_data = {
                "name": name,
                "quantity": quantity,
                "shopping_list_id": self.shopping_list_id,
            }

            logger.info(f"Adding item: {name} ({quantity})")
            response = self.session.post(f"{API_BASE}/items/", json=item_data)

            result = {
                "status_code": response.status_code,
                "success": response.status_code in [200, 201],
                "response_data": None,
                "error": None,
            }

            try:
                result["response_data"] = response.json()
            except:
                result["response_data"] = response.text

            if not result["success"]:
                result["error"] = f"HTTP {response.status_code}: {response.text}"

            logger.info(
                f"Item add result: {result['success']} (HTTP {result['status_code']})"
            )
            return result

        except Exception as e:
            logger.error(f"Error adding item: {e}")
            return {
                "status_code": 0,
                "success": False,
                "response_data": None,
                "error": str(e),
            }

    def test_czech_items(self):
        """Test adding Czech items that should trigger AI categorization."""
        test_items = [
            ("sůl do myčky", "1 ks"),  # The specific item mentioned in the task
            ("mléko", "1 l"),  # Simple Czech item
            ("chléb", "1 ks"),  # Another simple Czech item
            ("detergent na nádobí", "1 ks"),  # Cleaning product
        ]

        results = []
        for item_name, quantity in test_items:
            logger.info(f"\n{'='*50}")
            logger.info(f"Testing item: {item_name}")
            logger.info(f"{'='*50}")

            result = self.add_item(item_name, quantity)
            results.append({"item": item_name, "result": result})

            # Wait a bit between requests to allow logs to appear
            time.sleep(2)

        return results

    def run_test(self):
        """Run the complete test suite."""
        logger.info("Starting live fixes test...")

        # Step 1: Authenticate
        if not self.authenticate():
            logger.error("Authentication failed, cannot continue")
            return False

        # Step 2: Create shopping list
        if not self.create_shopping_list():
            logger.error("Failed to create shopping list, cannot continue")
            return False

        # Step 3: Test adding items
        logger.info("\nTesting Czech items that should trigger AI categorization...")
        results = self.test_czech_items()

        # Step 4: Summary
        logger.info(f"\n{'='*60}")
        logger.info("TEST SUMMARY")
        logger.info(f"{'='*60}")

        for test_result in results:
            item = test_result["item"]
            result = test_result["result"]
            status = "✓ PASS" if result["success"] else "✗ FAIL"
            logger.info(f"{status} - {item}: HTTP {result['status_code']}")
            if not result["success"] and result["error"]:
                logger.info(f"      Error: {result['error']}")

        logger.info(f"\n{'='*60}")
        logger.info("Check the backend logs above for:")
        logger.info("1. Any Gemini quota exceeded messages")
        logger.info("2. Ollama fallback activation")
        logger.info("3. UUID serialization errors in WebSocket messages")
        logger.info("4. Successful item categorization")
        logger.info(f"{'='*60}")

        return True


def main():
    """Main function to run the live test."""
    tester = LiveTester()
    try:
        tester.run_test()
    except KeyboardInterrupt:
        logger.info("\nTest interrupted by user")
    except Exception as e:
        logger.error(f"Test failed with error: {e}")


if __name__ == "__main__":
    main()
