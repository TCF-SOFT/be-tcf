from fastapi import Depends
from fastapi_users.authentication import RedisStrategy
from fastapi_users.authentication.strategy import AccessTokenDatabase, DatabaseStrategy

from src.api.auth.dependencies import get_access_tokens_db
from src.api.di.di import ResourceModule
from src.config import settings
from src.models.access_token import AccessToken


def get_redis_strategy() -> RedisStrategy:
    return RedisStrategy(
        ResourceModule().get_redis(),
        lifetime_seconds=settings.AUTH.LIFETIME_SECONDS,
    )


def get_database_strategy(
    access_tokens_db: AccessTokenDatabase[AccessToken] = Depends(get_access_tokens_db),
) -> DatabaseStrategy:
    """
    Пришлось создать дополнительную таблицу AccessToken, в сравнении с RedisStrategy
    Зависимости описаны в `dependencies.py`
    """
    return DatabaseStrategy(
        database=access_tokens_db,
        lifetime_seconds=settings.AUTH.LIFETIME_SECONDS,
    )
