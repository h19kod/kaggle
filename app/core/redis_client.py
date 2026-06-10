import json
import redis
from typing import Any, Optional
from app.core.config import settings

_pool: Optional[redis.ConnectionPool] = None


def get_redis_pool() -> redis.ConnectionPool:
    global _pool
    if _pool is None:
        _pool = redis.ConnectionPool(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True,
        )
    return _pool


def get_redis() -> redis.Redis:
    return redis.Redis(connection_pool=get_redis_pool())


class Cache:
    def __init__(self, redis_client: redis.Redis):
        self.client = redis_client

    def get(self, key: str) -> Any:
        data = self.client.get(key)
        if data:
            return json.loads(data)
        return None

    def set(self, key: str, value: Any, expire: int = 300) -> None:
        self.client.setex(key, expire, json.dumps(value))

    def delete(self, key: str) -> None:
        self.client.delete(key)

    def publish(self, channel: str, message: Any) -> None:
        self.client.publish(channel, json.dumps(message))

    def get_leaderboard(self, competition_id: int) -> Any:
        return self.get(f"leaderboard:{competition_id}")

    def set_leaderboard(self, competition_id: int, data: Any, expire: int = 60) -> None:
        self.set(f"leaderboard:{competition_id}", data, expire=expire)


cache = Cache(get_redis())
