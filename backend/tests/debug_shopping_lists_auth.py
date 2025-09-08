import requests
import json

# API URLs
BASE_URL = "http://localhost:8000"  # Adjust if your API is hosted elsewhere
LOGIN_URL = f"{BASE_URL}/api/v1/auth/jwt/login"
SHOPPING_LISTS_URL = f"{BASE_URL}/api/v1/shopping-lists/"

# Test user credentials
TEST_USER = {
    "email": "test@example.com",  # Replace with your test user
    "password": "Password123!",  # Replace with correct password
}


def test_shopping_lists():
    print("\n===== TESTING SHOPPING LISTS API =====\n")

    # Step 1: Login and get token
    print("Step 1: Logging in...")
    login_data = {"username": TEST_USER["email"], "password": TEST_USER["password"]}

    login_response = requests.post(
        LOGIN_URL,
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    print(f"Login status code: {login_response.status_code}")

    if login_response.status_code != 200:
        print(f"Login failed: {login_response.text}")
        return False

    token_data = login_response.json()
    token = token_data["access_token"]
    print(f"Token obtained: {token[:10]}...")

    # Step 2: Test retrieving shopping lists with different header formats

    # Method 1: Standard Bearer token
    print("\nMethod 1: Testing with standard Bearer token")
    response1 = requests.get(
        SHOPPING_LISTS_URL, headers={"Authorization": f"Bearer {token}"}
    )
    print(f"Status: {response1.status_code}")
    if response1.status_code == 200:
        data = response1.json()
        print(f"Success! Found {len(data)} shopping lists")
    else:
        print(f"Error: {response1.text}")

    # Method 2: Lowercase 'bearer'
    print("\nMethod 2: Testing with lowercase 'bearer'")
    response2 = requests.get(
        SHOPPING_LISTS_URL, headers={"Authorization": f"bearer {token}"}
    )
    print(f"Status: {response2.status_code}")
    if response2.status_code == 200:
        data = response2.json()
        print(f"Success! Found {len(data)} shopping lists")
    else:
        print(f"Error: {response2.text}")

    # Method 3: Just the token without prefix
    print("\nMethod 3: Testing with token only (no bearer prefix)")
    response3 = requests.get(SHOPPING_LISTS_URL, headers={"Authorization": token})
    print(f"Status: {response3.status_code}")
    if response3.status_code == 200:
        data = response3.json()
        print(f"Success! Found {len(data)} shopping lists")
    else:
        print(f"Error: {response3.text}")

    # Step 3: Test with URL variations
    print("\nTesting with URL without trailing slash")
    response4 = requests.get(
        SHOPPING_LISTS_URL.rstrip("/"), headers={"Authorization": f"Bearer {token}"}
    )
    print(f"Status: {response4.status_code}")
    print(f"URL after redirect: {response4.url}")
    if response4.status_code == 200:
        data = response4.json()
        print(f"Success! Found {len(data)} shopping lists")
    else:
        print(f"Error: {response4.text}")

    # Step 4: Test creating a shopping list
    print("\nTesting creating a shopping list")
    list_data = {"name": "Test Shopping List", "description": "Created via test script"}
    response5 = requests.post(
        SHOPPING_LISTS_URL, json=list_data, headers={"Authorization": f"Bearer {token}"}
    )
    print(f"Status: {response5.status_code}")
    if response5.status_code in [200, 201]:
        data = response5.json()
        print(f"Success! Created list with ID: {data.get('id')}")
    else:
        print(f"Error creating list: {response5.text}")

    print("\n===== TEST COMPLETED =====")


if __name__ == "__main__":
    test_shopping_lists()
