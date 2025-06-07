from fastapi import Request
from redis.asyncio import Redis


def get_redis_service(request: Request) -> Redis:
    """
    Dependency to get the Redis service instance from the request state.
    This allows for easy access to the Redis service in route handlers.
    Inited in the main app.
    """
    return request.app.state.redis
