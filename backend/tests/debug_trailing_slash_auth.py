"""
Debug script to test authentication with trailing slashes.

This script:
1. Registers a test user
2. Logs in and gets a token
3. Tests API endpoints both with and without trailing slashes
"""

import json
import requests
import random
import string

# Configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"

# Generate a random email to avoid conflicts
def random_email():
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"test_{random_str}@example.com"

# Test user data
user_data = {
    "email": random_email(),
    "password": "Password123!",
    "first_name": "Test",
    "last_name": "User"
}

def print_header(text):
    """Print a header with the given text"""
    print("\n" + "=" * 80)
    print(text)
    print("=" * 80)

def print_response(response):
    """Print the response in a formatted way"""
    print(f"Status: {response.status_code}")
    print(f"Headers: {json.dumps(dict(response.headers), indent=2)}")
    try:
        print(f"Body: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Body: {response.text}")

print_header(f"REGISTERING USER {user_data['email']}")
response = requests.post(
    f"{API_URL}/auth/register",
    json=user_data
)
print_response(response)
user_id = response.json().get("id")
print(f"User ID: {user_id}")

print_header("LOGGING IN")
response = requests.post(
    f"{API_URL}/auth/jwt/login",
    data={"username": user_data["email"], "password": user_data["password"]}
)
print_response(response)
token = response.json().get("access_token")
print(f"Token: {token[:10]}...")

headers = {
    "Authorization": f"Bearer {token}"
}

print_header("TESTING USER ENDPOINTS")
# Test "me" endpoint with trailing slash
print("\nGET /api/v1/users/me/")
response = requests.get(
    f"{API_URL}/users/me/",
    headers=headers
)
print_response(response)

# Test "me" endpoint without trailing slash
print("\nGET /api/v1/users/me")
response = requests.get(
    f"{API_URL}/users/me",
    headers=headers
)
print_response(response)

print_header("CREATING A TEST SHOPPING LIST")
# Create a shopping list
list_data = {
    "name": "Test List for Trailing Slash Test",
}
response = requests.post(
    f"{API_URL}/shopping-lists/",
    json=list_data,
    headers=headers
)
print_response(response)
list_id = response.json().get("id") if response.status_code == 200 else None
print(f"List ID: {list_id}")

print_header("TESTING SHOPPING LIST ENDPOINTS")
# Test with trailing slash
print("\nGET /api/v1/shopping-lists/")
response = requests.get(
    f"{API_URL}/shopping-lists/",
    headers=headers
)
print_response(response)

# Test without trailing slash
print("\nGET /api/v1/shopping-lists")
response = requests.get(
    f"{API_URL}/shopping-lists",
    headers=headers
)
print_response(response)

# Test specific list with trailing slash
if list_id:
    print(f"\nGET /api/v1/shopping-lists/{list_id}/")
    response = requests.get(
        f"{API_URL}/shopping-lists/{list_id}/",
        headers=headers
    )
    print_response(response)

    # Test specific list without trailing slash
    print(f"\nGET /api/v1/shopping-lists/{list_id}")
    response = requests.get(
        f"{API_URL}/shopping-lists/{list_id}",
        headers=headers
    )
    print_response(response)

print_header("SUMMARY")
print("This test demonstrates how FastAPI handles trailing slashes in URLs.")
print("If you see 307 redirects followed by 401 errors, it means authorization headers are being lost during redirects.")
print("The frontend should always use URLs with trailing slashes for consistency with FastAPI.")
