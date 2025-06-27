#!/usr/bin/env python3
"""
Debug cache behavior for AI services
"""
import asyncio
import sys
sys.path.insert(0, '/home/honzik/GitHub/FamilyCart/FamilyCart/backend')

from app.core.cache import cache_service

async def debug_cache():
    print("=== Testing Redis Cache Directly ===")
    
    # Test basic cache operations
    test_key = "test_key_12345"
    test_value = "test_value"
    
    try:
        # Set a value
        await cache_service.set(test_key, test_value, expire=60)
        print(f"✅ Set cache key '{test_key}' = '{test_value}'")
        
        # Get the value back
        retrieved_value = await cache_service.get(test_key)
        print(f"✅ Retrieved cache key '{test_key}' = '{retrieved_value}'")
        
        if retrieved_value == test_value:
            print("✅ Cache is working correctly!")
        else:
            print(f"❌ Cache mismatch: expected '{test_value}', got '{retrieved_value}'")
            
    except Exception as e:
        print(f"❌ Cache error: {e}")
        
    # Test the specific cache keys that AI service would use
    test_items = ["milk", "bread", "eggs"]
    
    print(f"\n=== Testing AI Cache Keys ===")
    for item in test_items:
        cache_key = f"category_suggestion:{item.lower().strip()}"
        cached_value = await cache_service.get(cache_key)
        print(f"Key: '{cache_key}' → Value: '{cached_value}'")

if __name__ == "__main__":
    asyncio.run(debug_cache())
