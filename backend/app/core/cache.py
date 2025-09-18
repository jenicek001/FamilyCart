import logging

import redis.asyncio as redis

from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    def __init__(self):
        self.redis_client = None

    async def setup(self):
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL, encoding="utf-8", decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("Successfully connected to Redis.")
        except Exception as e:
            logger.error(f"Error connecting to Redis: {e}")
            self.redis_client = None

    async def get(self, key: str):
        if not self.redis_client:
            return None
        return await self.redis_client.get(key)

    async def set(self, key: str, value: str, expire: int = 3600):
        if not self.redis_client:
            return
        await self.redis_client.set(key, value, ex=expire)

    async def close(self):
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis connection closed.")


cache_service = CacheService()
