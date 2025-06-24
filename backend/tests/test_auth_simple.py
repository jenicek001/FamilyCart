import requests
import uuid
import sys
import time

# Configuration
BASE_URL = "http://localhost:8000"

def test_auth_flow():
    """
    Test the complete authentication flow:
    1. Register a new user
    2. Login with the user credentials
    3. Access a protected endpoint (shopping lists)
    """
    # Generate random email to avoid conflicts
    test_email = f"test_{uuid.uuid4()}@example.com"
    test_password = "StrongPassword123!"
    
    print(f"Testing authentication flow with email: {test_email}")
    
    # Step 1: Register a new user
    register_data = {
        "email": test_email,
        "password": test_password,
        "first_name": "Test",
        "last_name": "User"
    }
    
    try:
        register_response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=register_data)
        print(f"Register response status: {register_response.status_code}")
        print(f"Register response body: {register_response.text}")
        
        if register_response.status_code != 201:
            print("❌ Registration failed")
            return False
        
        print("✅ User registered successfully")
        
        # Step 2: Login with the new user
        login_data = {
            "username": test_email,
            "password": test_password,
        }
        
        login_response = requests.post(
            f"{BASE_URL}/api/v1/auth/jwt/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        print(f"Login response status: {login_response.status_code}")
        print(f"Login response body: {login_response.text}")
        
        if login_response.status_code != 200:
            print("❌ Login failed")
            return False
        
        token_data = login_response.json()
        if "access_token" not in token_data:
            print("❌ No access token in response")
            return False
            
        access_token = token_data["access_token"]
        print("✅ Login successful, received access token")
        
        print(f"Access token: {access_token}")
        
        # Step 3: Access a protected endpoint (shopping lists)
        lists_response = requests.get(
            f"{BASE_URL}/api/v1/shopping-lists",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        print(f"Lists response status: {lists_response.status_code}")
        print(f"Lists response body: {lists_response.text}")
        
        if lists_response.status_code != 200:
            print("❌ Failed to access shopping lists")
            return False
            
        print("✅ Successfully accessed shopping lists with token")
        
        # Try without auth token (should fail)
        lists_no_auth_response = requests.get(f"{BASE_URL}/api/v1/shopping-lists")
        if lists_no_auth_response.status_code != 401:
            print("❌ Expected 401 when accessing without token")
            return False
            
        print("✅ Authentication check works - blocked unauthorized access")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = test_auth_flow()
    if success:
        print("\n✅✅✅ Authentication flow test passed successfully!")
        sys.exit(0)
    else:
        print("\n❌❌❌ Authentication flow test failed!")
        sys.exit(1)
