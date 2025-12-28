import redis
import json
import os
from typing import Optional, Any


class RedisClient:
    """Клиент для работы с Redis"""
    
    def __init__(self):
        try:
            self.client = redis.Redis(
                host=os.getenv('REDIS_HOST', 'cache'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                decode_responses=True,
                socket_timeout=2,
                socket_connect_timeout=2
            )
            self.client.ping()
            self.available = True
        except redis.RedisError:
            print("⚠️  Redis not available - caching disabled")
            self.available = False
    
    def get(self, key: str) -> Optional[dict]:
        if not self.available:
            return None
        try:
            data = self.client.get(key)
            if data:
                return json.loads(data)
        except (redis.RedisError, json.JSONDecodeError) as e:
            print(f"Redis get error: {e}")
        return None
    
    def set(self, key: str, value: Any, expire: int = 300) -> bool:
        if not self.available:
            return False
        try:
            self.client.setex(key, expire, json.dumps(value, default=str))
            return True
        except (redis.RedisError, TypeError) as e:
            print(f"Redis set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        if not self.available:
            return False
        try:
            self.client.delete(key)
            return True
        except redis.RedisError as e:
            print(f"Redis delete error: {e}")
            return False
    
    def ping(self) -> bool:
        if not self.available:
            return False
        try:
            return self.client.ping()
        except redis.RedisError:
            return False


redis_client = RedisClient()
