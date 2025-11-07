#!/usr/bin/env python3
"""
Debug Redis connection from cache service
"""
import asyncio
import sys

sys.path.insert(0, "/home/honzik/GitHub/FamilyCart/FamilyCart/backend")

from app.core.cache import cache_service


async def debug_redis_connection():
    print("=== Debugging Redis Connection in Cache Service ===")

    print(f"Cache service redis_client: {cache_service.redis_client}")

    if cache_service.redis_client is None:
        print("❌ Redis client is None! Setting up...")
        await cache_service.setup()
        print(f"After setup, redis_client: {cache_service.redis_client}")

    if cache_service.redis_client:
        try:
            # Test ping
            ping_result = await cache_service.redis_client.ping()
            print(f"✅ Ping result: {ping_result}")

            # Test direct set/get
            await cache_service.redis_client.set("direct_test", "direct_value", ex=60)
            direct_result = await cache_service.redis_client.get("direct_test")
            print(f"✅ Direct Redis set/get: {direct_result}")

            # Test through cache service methods
            await cache_service.set("service_test", "service_value", expire=60)
            service_result = await cache_service.get("service_test")
            print(f"✅ Cache service set/get: {service_result}")

        except Exception as e:
            print(f"❌ Redis operation failed: {e}")
            import traceback

            traceback.print_exc()
    else:
        print("❌ Still no Redis client after setup")


if __name__ == "__main__":
    asyncio.run(debug_redis_connection())
