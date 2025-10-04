"""Cache service using Redis"""
import json
from typing import Optional, Any
from datetime import timedelta


class CacheService:
    """Redis-based caching service"""

    def __init__(self, redis_client=None):
        """Initialize cache service"""
        self.redis = redis_client
        # TODO: Initialize Redis client

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.redis:
            return None

        value = await self.redis.get(key)
        if value:
            return json.loads(value)
        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[timedelta] = None
    ):
        """Set value in cache"""
        if not self.redis:
            return

        serialized = json.dumps(value)
        if ttl:
            await self.redis.setex(key, int(ttl.total_seconds()), serialized)
        else:
            await self.redis.set(key, serialized)

    async def delete(self, key: str):
        """Delete value from cache"""
        if self.redis:
            await self.redis.delete(key)
