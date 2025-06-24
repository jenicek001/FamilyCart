import requests
import json
from pprint import pprint

# API URLs
BASE_URL = "http://localhost:8000"
REGISTER_URL = f"{BASE_URL}/api/v1/auth/register"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/jwt/login"
SHOPPING_LISTS_URL = f"{BASE_URL}/api/v1/shopping-lists/"  # Note the trailing slash

# Test user credentials
TEST_USER = {
    "email": "test_shopper@example.com",
    "password": "Password123!",
    "first_name": "Test",
    "last_name": "Shopper"
}

# Step 1: Register a new user
def register_user():
    print("\n--- REGISTERING NEW USER ---")
    try:
        response = requests.post(REGISTER_URL, json=TEST_USER)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 201:
            print("User registered successfully!")
            return response.json()
        else:
            print(f"Registration failed: {response.text}")
            # If registration fails because user already exists, continue anyway
            return None
    except Exception as e:
        print(f"Error during registration: {e}")
        return None

# Step 2: Login and get access token
def login_user():
    print("\n--- LOGGING IN ---")
    login_data = {
        "username": TEST_USER["email"],
        "password": TEST_USER["password"]
    }
    
    try:
        # First, try with form data (what the API expects)
        response = requests.post(
            LOGIN_URL, 
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            token_data = response.json()
            print("Login successful!")
            return token_data["access_token"]
        else:
            print(f"Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"Error during login: {e}")
        return None

# Step 3: Create a shopping list
def create_shopping_list(token):
    print("\n--- CREATING SHOPPING LIST ---")
    shopping_list_data = {
        "name": "Test Shopping List",
        "description": "A test shopping list"
    }
    
    try:
        response = requests.post(
            SHOPPING_LISTS_URL,
            json=shopping_list_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200 or response.status_code == 201:
            print("Shopping list created successfully!")
            return response.json()
        else:
            print(f"Failed to create shopping list: {response.text}")
            return None
    except Exception as e:
        print(f"Error creating shopping list: {e}")
        return None

# Step 4: Get all shopping lists
def get_shopping_lists(token):
    print("\n--- GETTING SHOPPING LISTS ---")
    
    try:
        # Test with both URLs (with and without trailing slash)
        for url in [f"{BASE_URL}/api/v1/shopping-lists", f"{BASE_URL}/api/v1/shopping-lists/"]:
            print(f"\nTesting URL: {url}")
            
            response = requests.get(
                url,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                lists = response.json()
                print(f"Found {len(lists)} shopping lists:")
                for lst in lists:
                    print(f"  - {lst['name']}")
                return lists
            else:
                print(f"Failed to get shopping lists: {response.text}")
        
        return None
    except Exception as e:
        print(f"Error getting shopping lists: {e}")
        return None

# Main test flow
def run_test():
    # Register a new user (or continue if user already exists)
    register_result = register_user()
    
    # Login and get token
    token = login_user()
    if not token:
        print("Cannot proceed without authentication token")
        return
    
    # Print token for debugging
    print(f"\nToken: {token}")
    
    # Create a shopping list
    new_list = create_shopping_list(token)
    
    # Get all shopping lists
    all_lists = get_shopping_lists(token)

if __name__ == "__main__":
    run_test()
