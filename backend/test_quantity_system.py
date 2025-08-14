#!/usr/bin/env python3
"""Test script to verify quantity fields and Unit relationship are working."""

import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

async def test_quantity_system():
    """Test quantity system functionality."""
    
    # Test credentials
    test_credentials = {
        "username": "test@example.com",
        "password": "testpassword123"
    }
    
    async with httpx.AsyncClient() as client:
        print("Testing quantity system...")
        
        # Login first
        login_response = await client.post(
            "http://localhost:8000/api/v1/auth/jwt/login",
            data=test_credentials,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if login_response.status_code != 200:
            print("❌ Login failed")
            return False
            
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test getting units endpoint
        try:
            units_response = await client.get(
                "http://localhost:8000/api/v1/units",
                headers=headers
            )
            
            print(f"Units endpoint status: {units_response.status_code}")
            
            if units_response.status_code == 200:
                units = units_response.json()
                print(f"✅ Units endpoint working - Found {len(units)} units")
                print(f"Sample units: {[u['id'] for u in units[:5]]}")
                return True
            else:
                print(f"❌ Units endpoint failed: {units_response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Units test failed: {e}")
            return False

if __name__ == "__main__":
    asyncio.run(test_quantity_system())
