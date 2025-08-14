#!/usr/bin/env python3
"""
Test script that checks both versions of the shopping lists endpoint:
- With trailing slash (/api/v1/shopping-lists/)
- Without trailing slash (/api/v1/shopping-lists)

This helps confirm that both versions work correctly and don't suffer from
authentication issues or redirects.
"""

import requests
import json
import os
import sys
import time

# Set up colored output for better readability
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def check_both_endpoints():
    # Set the base URL - change this if you're running the server on a different host/port
    base_url = "http://localhost:8000"
    
    print(f"{Colors.HEADER}Shopping Lists Endpoint Checker{Colors.ENDC}")
    print(f"{Colors.BOLD}--------------------------------{Colors.ENDC}\n")
    
    # Step 1: Login to get a token
    print(f"{Colors.BOLD}Step 1: Authenticating and getting token...{Colors.ENDC}")
    login_url = f"{base_url}/api/v1/auth/jwt/login"
    
    # Get credentials from environment variables or prompt the user
    username = os.environ.get("API_DEBUG_USERNAME")
    password = os.environ.get("API_DEBUG_PASSWORD")
    
    if not username:
        username = input("Enter username: ")
    if not password:
        import getpass
        password = getpass.getpass("Enter password: ")
    
    login_data = {
        "username": username,
        "password": password
    }
    
    try:
        login_response = requests.post(login_url, data=login_data)
        login_response.raise_for_status()
        
        token = login_response.json().get("access_token")
        if not token:
            raise Exception("No access token in response")
        
        print(f"{Colors.OKGREEN}Authentication successful! Token received.{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}Authentication failed: {str(e)}{Colors.ENDC}")
        print(f"Response: {login_response.text if 'login_response' in locals() else 'No response'}")
        return
    
    # Set authorization header for subsequent requests
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # Step 2: Test both endpoints
    print(f"\n{Colors.BOLD}Step 2: Testing shopping lists endpoints...{Colors.ENDC}")
    
    # Test both with and without trailing slash using default requests
    endpoints_to_test = [
        {"url": f"{base_url}/api/v1/shopping-lists", "name": "No trailing slash (default)"},
        {"url": f"{base_url}/api/v1/shopping-lists/", "name": "With trailing slash (default)"},
    ]
    
    for endpoint in endpoints_to_test:
        print(f"\n{Colors.BOLD}Testing {endpoint['name']}...{Colors.ENDC}")
        
        try:
            print(f"GET {endpoint['url']}")
            print(f"Headers: {headers}")
            
            # Make the request with expanded debugging
            start_time = time.time()
            response = requests.get(endpoint['url'], headers=headers)
            duration = time.time() - start_time
            
            # Check response
            print(f"Response Status: {response.status_code}")
            print(f"Response Time: {duration:.2f}s")
            print(f"Final URL: {response.url}")
            
            # Check for redirects
            if len(response.history) > 0:
                print(f"{Colors.WARNING}Request was redirected!{Colors.ENDC}")
                for r in response.history:
                    print(f" - {r.status_code}: {r.url} -> {r.headers.get('Location')}")
            
            # Print response body if successful
            if response.status_code == 200:
                print(f"{Colors.OKGREEN}Success!{Colors.ENDC}")
                try:
                    json_response = response.json()
                    print(f"Data: {json.dumps(json_response, indent=2)}")
                    num_lists = len(json_response) if isinstance(json_response, list) else "unknown"
                    print(f"Found {num_lists} shopping list(s)")
                except json.JSONDecodeError:
                    print(f"{Colors.WARNING}Response is not valid JSON: {response.text}{Colors.ENDC}")
            else:
                print(f"{Colors.FAIL}Error: {response.status_code}{Colors.ENDC}")
                print(f"Response: {response.text}")
        except Exception as e:
            print(f"{Colors.FAIL}Request failed: {str(e)}{Colors.ENDC}")
    
    # Step 3: Test with disable redirects to see actual behavior
    print(f"\n{Colors.BOLD}Step 3: Testing with allow_redirects=False...{Colors.ENDC}")
    
    # Same endpoints but with redirects disabled
    for endpoint in endpoints_to_test:
        try:
            print(f"\nTesting {endpoint['name']} with redirects disabled...")
            
            # Make the request with redirects disabled
            response = requests.get(endpoint['url'], headers=headers, allow_redirects=False)
            
            # Check response
            print(f"Response Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if 300 <= response.status_code < 400:  # Redirect status code
                print(f"{Colors.WARNING}Redirect detected! Location: {response.headers.get('Location')}{Colors.ENDC}")
            elif response.status_code == 200:
                print(f"{Colors.OKGREEN}Direct 200 response (no redirect needed){Colors.ENDC}")
                try:
                    json_response = response.json()
                    print(f"Data: {json.dumps(json_response, indent=2)}")
                except json.JSONDecodeError:
                    print(f"{Colors.WARNING}Response is not valid JSON: {response.text}{Colors.ENDC}")
            else:
                print(f"{Colors.FAIL}Error: {response.status_code}{Colors.ENDC}")
                print(f"Response: {response.text}")
        except Exception as e:
            print(f"{Colors.FAIL}Request failed: {str(e)}{Colors.ENDC}")
    
    print(f"\n{Colors.HEADER}Test complete!{Colors.ENDC}")

if __name__ == "__main__":
    check_both_endpoints()
