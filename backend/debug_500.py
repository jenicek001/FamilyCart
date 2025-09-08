#!/usr/bin/env python3
"""
Simple debug test to isolate the 500 error
"""
import requests


def debug_500_error():
    base_url = "http://localhost:8000"

    # Login as Berta
    login_data = {"username": "berta.stepanova@gmail.com", "password": "berta"}

    login_response = requests.post(
        f"{base_url}/api/v1/auth/jwt/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    if login_response.status_code != 200:
        print(f"Login failed: {login_response.text}")
        return

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    print("✅ Login successful")

    # Test 1: Try to get all shopping lists
    print("Testing GET /shopping-lists/...")
    lists_response = requests.get(f"{base_url}/api/v1/shopping-lists/", headers=headers)
    print(f"Status: {lists_response.status_code}")
    if lists_response.status_code != 200:
        print(f"Error: {lists_response.text}")
        return

    lists = lists_response.json()
    print(f"✅ Got {len(lists)} shopping lists")

    # Find list 11
    list_11 = None
    for lst in lists:
        if lst["id"] == 11:
            list_11 = lst
            break

    if not list_11:
        print("❌ List 11 not found in user's lists")
        return

    print(f"✅ Found list 11: {list_11['name']}")

    # Test 2: Try to get specific list
    print("Testing GET /shopping-lists/11...")
    list_response = requests.get(
        f"{base_url}/api/v1/shopping-lists/11", headers=headers
    )
    print(f"Status: {list_response.status_code}")
    if list_response.status_code != 200:
        print(f"Error: {list_response.text}")
        return

    print("✅ Successfully accessed list 11")

    # Test 3: Try to get items from list 11 using items endpoint
    print("Testing GET /items/list/11...")
    items_response = requests.get(f"{base_url}/api/v1/items/list/11", headers=headers)
    print(f"Status: {items_response.status_code}")
    if items_response.status_code != 200:
        print(f"Error: {items_response.text}")
    else:
        items = items_response.json()
        print(f"✅ Got {len(items)} items from list 11")


if __name__ == "__main__":
    debug_500_error()
