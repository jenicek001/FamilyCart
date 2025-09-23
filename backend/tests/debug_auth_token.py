import json
import sys
from urllib.parse import urljoin

import requests


def print_header(text):
    print("\n" + "=" * 60)
    print(f"{text.center(60)}")
    print("=" * 60 + "\n")


def debug_token_issue(
    base_url="http://localhost:8000", email="test@example.com", password="Password123!"
):
    """
    Debug token authentication issues with FastAPI backend
    """
    print_header("FastAPI Authentication Debugger")

    # Step 1: Login to get token
    print("Step 1: Login to get token")
    login_endpoint = urljoin(base_url, "/api/v1/auth/jwt/login")
    print(f"POST {login_endpoint}")

    try:
        login_response = requests.post(
            login_endpoint,
            data={"username": email, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        print(f"Status Code: {login_response.status_code}")

        if login_response.status_code != 200:
            print(f"Login failed: {login_response.text}")
            sys.exit(1)

        login_data = login_response.json()
        token = login_data.get("access_token")

        if not token:
            print("Error: No token in response")
            sys.exit(1)

        print(f"Token received: {token[:15]}...")

    except Exception as e:
        print(f"Error during login: {e}")
        sys.exit(1)

    # Step 2: Test /users/me endpoint
    print("\nStep 2: Test /api/v1/users/me endpoint")
    me_endpoint = urljoin(base_url, "/api/v1/users/me")
    print(f"GET {me_endpoint}")

    try:
        # Try with various header formats
        headers_to_test = [
            {"Authorization": f"Bearer {token}"},
            {"authorization": f"Bearer {token}"},
            {"Authorization": f"bearer {token}"},
            {"Authorization": token},
        ]

        for i, headers in enumerate(headers_to_test, 1):
            print(f"\nTest {i}: Using headers: {headers}")
            me_response = requests.get(me_endpoint, headers=headers)
            print(f"Status Code: {me_response.status_code}")

            if me_response.status_code == 200:
                print("✅ Success!")
                user_data = me_response.json()
                print(f"User: {user_data.get('email')}")
            else:
                print(f"❌ Failed: {me_response.text}")

    except Exception as e:
        print(f"Error testing /users/me: {e}")

    # Step 3: Test shopping-lists endpoint
    print("\nStep 3: Test /api/v1/shopping-lists/ endpoint")
    lists_endpoint = urljoin(base_url, "/api/v1/shopping-lists/")
    print(f"GET {lists_endpoint}")

    try:
        # Use the format that worked for /users/me
        lists_response = requests.get(
            lists_endpoint, headers={"Authorization": f"Bearer {token}"}
        )

        print(f"Status Code: {lists_response.status_code}")

        if lists_response.status_code == 200:
            lists_data = lists_response.json()
            print(f"✅ Success! Found {len(lists_data)} lists")
            for lst in lists_data:
                print(f"- {lst.get('name')}")
        else:
            print(f"❌ Failed: {lists_response.text}")

    except Exception as e:
        print(f"Error testing shopping-lists: {e}")

    # Step 4: Create a new shopping list
    print("\nStep 4: Create a new shopping list")

    try:
        new_list = {"name": "Test List", "description": "Created by debug script"}

        create_response = requests.post(
            lists_endpoint, json=new_list, headers={"Authorization": f"Bearer {token}"}
        )

        print(f"Status Code: {create_response.status_code}")

        if create_response.status_code in [200, 201]:
            new_list_data = create_response.json()
            print(f"✅ Success! Created list: {new_list_data.get('name')}")
        else:
            print(f"❌ Failed: {create_response.text}")

    except Exception as e:
        print(f"Error creating list: {e}")

    print_header("Debugging Complete")


if __name__ == "__main__":
    debug_token_issue()
