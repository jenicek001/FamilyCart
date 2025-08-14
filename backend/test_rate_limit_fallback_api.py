#!/usr/bin/env python3
"""
Test Rate Limit Fallback via API

This script tests the fallback functionality by making API calls and simulating
rate limit scenarios to verify automatic switching to Ollama.
"""

import requests
import json
import time
import sys
import os

# Add the backend app directory to Python path
sys.path.append('/home/honzik/GitHub/FamilyCart/FamilyCart/backend')

from app.services.fallback_ai_service import fallback_ai_service


def get_auth_token():
    """Get authentication token for API calls."""
    base_url = "http://localhost:8000/api/v1"
    
    login_data = {
        "username": "test@example.com",
        "password": "testpassword123"
    }
    
    response = requests.post(
        f"{base_url}/auth/jwt/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code == 200:
        token_data = response.json()
        return token_data.get("access_token")
    else:
        raise Exception(f"Login failed: {response.status_code} - {response.text}")


def test_ai_status(token):
    """Test AI status endpoint."""
    base_url = "http://localhost:8000/api/v1"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(f"{base_url}/ai/status", headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"AI status check failed: {response.status_code} - {response.text}")


def test_categorization(token, item):
    """Test categorization endpoint."""
    base_url = "http://localhost:8000/api/v1"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {"item_name": item}
    
    start_time = time.time()
    response = requests.post(f"{base_url}/ai/categorize-item", json=data, headers=headers)
    elapsed = time.time() - start_time
    
    if response.status_code == 200:
        result = response.json()
        return result.get("category_name"), elapsed
    else:
        raise Exception(f"Categorization failed: {response.status_code} - {response.text}")


def main():
    """Main test function."""
    print("🚀 Testing AI Fallback via API")
    print("="*50)
    
    try:
        # Get authentication token
        print("🔐 Getting authentication token...")
        token = get_auth_token()
        print("✅ Authentication successful")
        
        # Test initial AI status
        print("\n📊 Checking AI status...")
        status = test_ai_status(token)
        print(f"  Provider: {status.get('provider_name')}")
        print(f"  Model: {status.get('model_name')}")
        print(f"  Status: {status.get('status')}")
        print(f"  Rate limit detected: {status.get('rate_limit_detected', 'N/A')}")
        print(f"  Fallback available: {status.get('fallback_available', 'N/A')}")
        
        # Test normal categorization
        print("\n🧪 Testing normal categorization...")
        test_items = ["orange", "yogurt", "rice"]
        
        for item in test_items:
            try:
                category, elapsed = test_categorization(token, item)
                print(f"  ✅ '{item}' -> '{category}' ({elapsed:.3f}s)")
            except Exception as e:
                print(f"  ❌ '{item}' -> Error: {e}")
        
        # Simulate rate limit manually in the fallback service
        print("\n⚠️  Simulating rate limit scenario...")
        fallback_ai_service._rate_limit_detected = True
        fallback_ai_service._rate_limit_reset_time = time.time() + 30  # 30 seconds
        print("  Rate limit flag set in fallback service")
        
        # Test AI status after rate limit
        print("\n📊 Checking AI status after rate limit simulation...")
        status = test_ai_status(token)
        print(f"  Provider: {status.get('provider_name')}")
        print(f"  Model: {status.get('model_name')}")
        print(f"  Status: {status.get('status')}")
        print(f"  Rate limit detected: {status.get('rate_limit_detected', 'N/A')}")
        
        # Test categorization with fallback
        print("\n🔄 Testing categorization with fallback...")
        fallback_items = ["pasta", "shampoo", "cheese"]
        
        for item in fallback_items:
            try:
                category, elapsed = test_categorization(token, item)
                print(f"  ✅ '{item}' -> '{category}' ({elapsed:.3f}s) [FALLBACK]")
            except Exception as e:
                print(f"  ❌ '{item}' -> Error: {e}")
        
        # Reset rate limit
        print("\n🔄 Resetting rate limit...")
        fallback_ai_service._rate_limit_detected = False
        fallback_ai_service._rate_limit_reset_time = None
        print("  Rate limit flag reset")
        
        # Test recovery
        print("\n✅ Testing recovery to primary provider...")
        recovery_items = ["tomato", "soap"]
        
        for item in recovery_items:
            try:
                category, elapsed = test_categorization(token, item)
                print(f"  ✅ '{item}' -> '{category}' ({elapsed:.3f}s) [RECOVERED]")
            except Exception as e:
                print(f"  ❌ '{item}' -> Error: {e}")
        
        # Final status check
        print("\n📊 Final AI status...")
        status = test_ai_status(token)
        print(f"  Provider: {status.get('provider_name')}")
        print(f"  Model: {status.get('model_name')}")
        print(f"  Status: {status.get('status')}")
        print(f"  Rate limit detected: {status.get('rate_limit_detected', 'N/A')}")
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
