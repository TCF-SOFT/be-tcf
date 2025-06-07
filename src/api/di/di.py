from redis.asyncio import Redis

from src.common.services.redis_service import RedisService
from src.utils.singleton import SingletonMeta


class ResourceModule(metaclass=SingletonMeta):
    """
    Class encapsulating the services:
    - RedisService
    """

    def __init__(self, redis_service: RedisService):
        self.redis_service = redis_service
        self.redis = redis_service.get_redis()

    def get_redis_service(self) -> RedisService:
        return self.redis_service

    def get_redis(self) -> Redis:
        return self.redis
