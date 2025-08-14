#!/usr/bin/env python3
"""
Debug script to check Redis configuration loading
"""
import sys
import os

# Add backend to path
sys.path.insert(0, '/home/honzik/GitHub/FamilyCart/FamilyCart/backend')

try:
    from app.core.config import settings
    
    print("=== Debug Redis Configuration ===")
    print(f"REDIS_HOST: {settings.REDIS_HOST}")
    print(f"REDIS_PORT: {settings.REDIS_PORT}")
    print(f"REDIS_PASSWORD: {settings.REDIS_PASSWORD}")
    print(f"REDIS_URL: {settings.REDIS_URL}")
    
    # Check environment variables directly
    print("\n=== Environment Variables ===")
    print(f"REDIS_PASSWORD (env): {os.getenv('REDIS_PASSWORD')}")
    print(f"REDIS_HOST (env): {os.getenv('REDIS_HOST')}")
    print(f"REDIS_PORT (env): {os.getenv('REDIS_PORT')}")
    
    # Check .env file loading
    print(f"\n=== Config File ===")
    print(f"Config env_file: {settings.Config.env_file}")
    
    # Test Redis connection directly
    print(f"\n=== Direct Redis Connection Test ===")
    try:
        import redis.asyncio as redis
        
        # Test the exact URL that the backend is using
        redis_url = settings.REDIS_URL
        print(f"Testing connection to: {redis_url}")
        
        # Create connection
        redis_client = redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
        
        # Test ping (this will run synchronously for testing)
        import asyncio
        async def test_redis():
            try:
                result = await redis_client.ping()
                print(f"✅ Redis ping successful: {result}")
                await redis_client.close()
                return True
            except Exception as e:
                print(f"❌ Redis ping failed: {e}")
                await redis_client.close()
                return False
        
        # Run the async test
        success = asyncio.run(test_redis())
        
    except Exception as e:
        print(f"❌ Redis connection setup failed: {e}")
        
    # Test with redis-py (sync version) for comparison
    print(f"\n=== Sync Redis Test ===")
    try:
        import redis
        
        # Parse the URL components
        host = settings.REDIS_HOST
        port = settings.REDIS_PORT
        password = settings.REDIS_PASSWORD
        
        print(f"Connecting to Redis with:")
        print(f"  Host: {host}")
        print(f"  Port: {port}")
        print(f"  Password: {'***' if password else 'None'}")
        
        # Create sync client
        sync_client = redis.Redis(host=host, port=port, password=password, decode_responses=True)
        result = sync_client.ping()
        print(f"✅ Sync Redis ping successful: {result}")
        sync_client.close()
        
    except Exception as e:
        print(f"❌ Sync Redis connection failed: {e}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
