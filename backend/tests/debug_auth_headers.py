import requests
import uuid
import json

# Configuration
BASE_URL = "http://localhost:8000"

def test_auth_and_api_access():
    """
    Test full authentication flow and API access:
    1. Register a new user
    2. Login to obtain token
    3. Test API access with token
    4. Debug token format and headers
    """
    # Generate random email to avoid conflicts
    test_email = f"test_{uuid.uuid4()}@example.com"
    test_password = "StrongPassword123!"
    
    print(f"\n===== Testing with email: {test_email} =====")
    
    # Step 1: Register a new user
    register_data = {
        "email": test_email,
        "password": test_password,
        "first_name": "Test",
        "last_name": "User"
    }
    
    try:
        register_response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=register_data)
        print(f"\n1. REGISTER - Status: {register_response.status_code}")
        print(f"Response: {register_response.text}")
        
        if register_response.status_code != 201:
            print("❌ Registration failed")
            return False
        
        print("✅ Registration successful")
        
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
        
        print(f"\n2. LOGIN - Status: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        
        if login_response.status_code != 200:
            print("❌ Login failed")
            return False
        
        token_data = login_response.json()
        if "access_token" not in token_data:
            print("❌ No access token in response")
            return False
            
        access_token = token_data["access_token"]
        token_type = token_data.get("token_type", "bearer")
        print(f"✅ Login successful, received token type: {token_type}")
        
        # Debug the token
        print(f"\n=== TOKEN DETAILS ===")
        print(f"Token: {access_token}")
        print(f"Token type: {token_type}")
        print(f"Auth header format: {token_type} {access_token}")
        
        # Step 3: Check if axios sets the header correctly
        auth_header = f"{token_type} {access_token}"
        
        # Step 4: Test multiple API endpoints with token
        endpoints = [
            "/api/v1/users/me",
            "/api/v1/shopping-lists/",
        ]
        
        print("\n=== TESTING API ENDPOINTS ===")
        for endpoint in endpoints:
            response = requests.get(
                f"{BASE_URL}{endpoint}",
                headers={"Authorization": auth_header}
            )
            print(f"\nEndpoint: {endpoint}")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}..." if len(response.text) > 200 else f"Response: {response.text}")
            
            if response.status_code == 200:
                print("✅ Access successful")
            else:
                print("❌ Access failed")
                
        # Step 5: Test the same endpoints with different header formats
        print("\n=== TESTING DIFFERENT AUTH HEADER FORMATS ===")
        
        header_formats = [
            {"Authorization": auth_header},
            {"Authorization": f"Bearer {access_token}"},
            {"Authorization": f"bearer {access_token}"},
            {"Authorization": f"{access_token}"},
        ]
        
        for i, headers in enumerate(header_formats):
            print(f"\nTest {i+1}: Headers = {headers}")
            response = requests.get(
                f"{BASE_URL}/api/v1/shopping-lists/",
                headers=headers
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("✅ Access successful with this header format")
            else:
                print("❌ Access failed with this header format")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_auth_and_api_access()
    print("\n===== TEST SUMMARY =====")
    if success:
        print("✅ All steps completed - review console output for details")
    else:
        print("❌ Test failed at one or more steps")
