from redis.asyncio import Redis

from api.di.redis_service import RedisService
from utils.singleton import SingletonMeta


class ResourceModule(metaclass=SingletonMeta):
    """
    Class encapsulating the services:
    - RedisService
    """

    def __init__(self, redis: RedisService):
        self.redis = redis.get_redis()

    def get_redis(self) -> Redis:
        return self.redis
