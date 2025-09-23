import json
import os
import sys

import requests

# Add the parent directory to sys.path to be able to import from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings


# Colors for terminal output
class Colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


# Main debug function
def debug_shopping_lists_api():
    # Set the base URL - change this if you're running the server on a different host/port
    base_url = "http://localhost:8000"

    print(f"{Colors.HEADER}FamilyCart API Debug Tool - Shopping Lists API{Colors.ENDC}")
    print(f"{Colors.BOLD}----------------------------------------------{Colors.ENDC}\n")

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

    login_data = {"username": username, "password": password}

    try:
        login_response = requests.post(login_url, data=login_data)
        login_response.raise_for_status()  # Raise exception for 4xx/5xx responses

        token = login_response.json().get("access_token")
        if not token:
            raise Exception("No access token in response")

        print(
            f"{Colors.OKGREEN}Authentication successful! Token received.{Colors.ENDC}"
        )
        print(f"Token: {token[:15]}...{token[-5:]}")
    except Exception as e:
        print(f"{Colors.FAIL}Authentication failed: {str(e)}{Colors.ENDC}")
        print(
            f"Response: {login_response.text if 'login_response' in locals() else 'No response'}"
        )
        return

    # Set authorization header for subsequent requests
    headers = {"Authorization": f"Bearer {token}"}

    # Step 2: Test user info endpoint
    print(f"\n{Colors.BOLD}Step 2: Testing /api/v1/users/me endpoint...{Colors.ENDC}")

    # Test both with and without trailing slash
    endpoints_to_test = [
        {"url": f"{base_url}/api/v1/users/me", "name": "User info (no trailing slash)"},
        {"url": f"{base_url}/api/v1/users/me/", "name": "User info (trailing slash)"},
    ]

    for endpoint in endpoints_to_test:
        try:
            print(f"Testing {endpoint['name']}...")
            response = requests.get(endpoint["url"], headers=headers)

            print(f"Status code: {response.status_code}")
            if response.status_code == 200:
                print(f"{Colors.OKGREEN}Success!{Colors.ENDC}")
                print(f"User data: {json.dumps(response.json(), indent=2)}")
            else:
                print(
                    f"{Colors.WARNING}Request completed but returned non-200 status code.{Colors.ENDC}"
                )
                print(f"Response: {response.text}")
        except Exception as e:
            print(f"{Colors.FAIL}Request failed: {str(e)}{Colors.ENDC}")

    # Step 3: Test shopping lists endpoint
    print(f"\n{Colors.BOLD}Step 3: Testing shopping lists endpoints...{Colors.ENDC}")

    # Test both with and without trailing slash
    endpoints_to_test = [
        {
            "url": f"{base_url}/api/v1/shopping-lists",
            "name": "Shopping lists (no trailing slash)",
        },
        {
            "url": f"{base_url}/api/v1/shopping-lists/",
            "name": "Shopping lists (trailing slash)",
        },
    ]

    for endpoint in endpoints_to_test:
        try:
            print(f"\nTesting {endpoint['name']}...")

            # Print full request details for debugging
            print(f"Request URL: {endpoint['url']}")
            print(f"Request Headers: {headers}")

            # Make the request with expanded debugging
            session = requests.Session()
            response = session.get(endpoint["url"], headers=headers)

            # Analyze response
            print(f"Response Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")

            # Check for redirects
            if response.history:
                print(f"{Colors.WARNING}Request was redirected!{Colors.ENDC}")
                for r in response.history:
                    print(f" - {r.status_code}: {r.url} -> {r.headers.get('Location')}")
                    print(f"   Headers after redirect: {dict(r.headers)}")
                print(f"Final URL: {response.url}")

            # Print response body
            try:
                json_response = response.json()
                print(f"Response Body: {json.dumps(json_response, indent=2)}")

                if response.status_code == 200:
                    print(f"{Colors.OKGREEN}Success!{Colors.ENDC}")
                    num_lists = (
                        len(json_response)
                        if isinstance(json_response, list)
                        else "unknown"
                    )
                    print(f"Found {num_lists} shopping list(s)")
                else:
                    print(
                        f"{Colors.WARNING}Request completed but returned non-200 status code.{Colors.ENDC}"
                    )
            except json.JSONDecodeError:
                print(
                    f"{Colors.WARNING}Response is not valid JSON: {response.text}{Colors.ENDC}"
                )
        except Exception as e:
            print(f"{Colors.FAIL}Request failed: {str(e)}{Colors.ENDC}")

    # Step 4: Test OPTIONS request to check allowed methods
    print(
        f"\n{Colors.BOLD}Step 4: Testing OPTIONS request on shopping lists endpoint...{Colors.ENDC}"
    )

    try:
        options_url = f"{base_url}/api/v1/shopping-lists/"
        options_response = requests.options(options_url)

        print(f"Status code: {options_response.status_code}")
        print(f"Allow header: {options_response.headers.get('Allow', 'Not present')}")
        print(
            f"Access-Control-Allow-Methods: {options_response.headers.get('Access-Control-Allow-Methods', 'Not present')}"
        )
        print(f"All headers: {dict(options_response.headers)}")
    except Exception as e:
        print(f"{Colors.FAIL}OPTIONS request failed: {str(e)}{Colors.ENDC}")

    print(f"\n{Colors.HEADER}Debug complete!{Colors.ENDC}")


if __name__ == "__main__":
    debug_shopping_lists_api()
