from typing import AsyncGenerator

from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config import settings


class DatabaseHelper:
    def __init__(
        self,
        url: str,
        is_test: bool = False,
        future=True,
        echo=False,
        pool_pre_ping=True,
        echo_pool: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10,
    ) -> None:
        database_params: dict = {}

        if is_test:
            url = settings.DB.TEST_PSQL_URL
            database_params = {"poolclass": NullPool}

        self.engine: AsyncEngine = create_async_engine(
            url=url,
            future=future,
            echo=echo,
            pool_pre_ping=pool_pre_ping,
            echo_pool=echo_pool,
            pool_size=pool_size,
            max_overflow=max_overflow,
            **database_params,
        )
        self.AsyncSessionFactory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    async def dispose(self) -> None:
        await self.engine.dispose()

    @property
    async def session_getter(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.AsyncSessionFactory() as session:
            yield session


# db_helper = DatabaseHelper(
#     url=settings.DB.PSQL_URL,
#     is_test=settings.MODE == "TEST",
#     future=True,
#     echo=settings.DB.echo,
#     pool_pre_ping=True,
#     echo_pool=settings.DB.echo_pool,
#     pool_size=settings.DB.pool_size,
#     max_overflow=settings.DB.max_overflow,
# )
