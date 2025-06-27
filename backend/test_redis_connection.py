#!/usr/bin/env python3
"""
Test Redis connection with the exact same setup as the backend
"""
import asyncio
from app.core.config import settings

async def test_redis_connection():
    print("=== Testing Redis Connection ===")
    print(f"REDIS_URL: {settings.REDIS_URL}")
    
    try:
        import redis.asyncio as redis
        
        # Use the exact same setup as in app/core/cache.py
        redis_client = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
        
        print("Attempting to ping Redis...")
        result = await redis_client.ping()
        print(f"✅ SUCCESS: Redis ping returned: {result}")
        
        # Test a basic operation
        await redis_client.set("test_key", "test_value", ex=10)
        value = await redis_client.get("test_key")
        print(f"✅ SUCCESS: Set/Get test: {value}")
        
        await redis_client.close()
        
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_redis_connection())
