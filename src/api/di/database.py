from collections.abc import AsyncGenerator

from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config.config import settings
from utils.logging import logger

DATABASE_URL = settings.DB.PSQL_URL


DATABASE_PARAMS = {"poolclass": NullPool} if settings.MODE == "TEST" else {}

engine = create_async_engine(
    DATABASE_URL,
    future=True,
    echo=False,  # Set to True to see the SQL queries in logs
    pool_pre_ping=True,
    **DATABASE_PARAMS,
)

# expire_on_commit=False will prevent attributes from being expired
# after commit.
AsyncSessionFactory = async_sessionmaker(
    engine,
    autoflush=False,
    expire_on_commit=False,
)


# Dependency for FastAPI Users
async def get_auth_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionFactory() as session:
        yield session


# Dependency for DAO
async def get_db() -> AsyncGenerator:
    async with AsyncSessionFactory() as session:
        logger.debug(f"ASYNC Pool: {engine.pool.status()}")
        async with session.begin():
            yield session


async def dispose() -> None:
    await engine.dispose()
