import redis
import json
from typing import Optional, Any
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

class RedisCache:
    def __init__(self):
        self.client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    
    def get(self, key: str) -> Optional[Any]:
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
        return None
    
    def set(self, key: str, value: Any, ttl: int = None):
        try:
            ttl = ttl or settings.CACHE_TTL
            self.client.setex(key, ttl, json.dumps(value))
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    def delete(self, key: str):
        try:
            self.client.delete(key)
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
    
    def invalidate_pattern(self, pattern: str):
        """Invalidate all keys matching pattern"""
        try:
            for key in self.client.scan_iter(match=pattern):
                self.client.delete(key)
        except Exception as e:
            logger.error(f"Cache invalidate error: {e}")
    
    def acquire_lock(self, lock_name: str, timeout: int = 10) -> bool:
        try:
            return self.client.set(f"lock:{lock_name}", "1", nx=True, ex=timeout)
        except Exception as e:
            logger.error(f"Lock acquire error: {e}")
            return False
    
    def release_lock(self, lock_name: str):
        try:
            self.client.delete(f"lock:{lock_name}")
        except Exception as e:
            logger.error(f"Lock release error: {e}")
    
    def publish(self, channel: str, message: dict):
        try:
            self.client.publish(channel, json.dumps(message))
        except Exception as e:
            logger.error(f"Publish error: {e}")

cache = RedisCache()