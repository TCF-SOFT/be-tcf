from redis.asyncio import ConnectionPool
from redis.asyncio.client import Redis

from src.config import settings


class RedisService:
    def __init__(self):
        __redis_pool = self._redis_connection_pool()
        self.redis = self._create_redis(__redis_pool)

    @staticmethod
    def _redis_connection_pool() -> ConnectionPool:
        return ConnectionPool(
            host=settings.REDIS.REDIS_HOST,
            port=settings.REDIS.REDIS_PORT,
            db=settings.REDIS.REDIS_DB,
        )

    @staticmethod
    def _create_redis(pool: ConnectionPool) -> Redis:
        return Redis(
            connection_pool=pool, ssl=True, encoding="utf-8", decode_responses=True
        )

    async def close(self):
        await self.redis.close()
        await self.redis.connection_pool.disconnect()

    def get_redis(self) -> Redis:
        return self.redis
