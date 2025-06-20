import asyncio
import json
from pathlib import Path
from typing import AsyncGenerator, Generator
from unittest import mock

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from src.models import Category, Offer, Product, SubCategory
from src.models.base import Base
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer


# -------------------------------
# 🔌 Database & Redis containers
# -------------------------------
@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:17") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def redis_container():
    with RedisContainer("redis:7") as redis:
        yield redis


# -------------------------------
# 🛠 DB Engine & Session factory
# -------------------------------
@pytest.fixture(scope="session")
def db_engine(postgres_container) -> Generator[AsyncEngine, None, None]:
    user = postgres_container.username
    password = postgres_container.password
    db = postgres_container.dbname
    host = postgres_container.get_container_host_ip()
    port = postgres_container.get_exposed_port(postgres_container.port)

    url = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"

    engine = create_async_engine(url, echo=False, future=True)
    yield engine
    asyncio.get_event_loop().run_until_complete(engine.dispose())


@pytest.fixture(scope="session")
def db_session_factory(db_engine):
    return async_sessionmaker(bind=db_engine, expire_on_commit=False)


# -------------------------------
# DB Schema Setup & Seeding
# -------------------------------
@pytest.fixture(scope="session", autouse=True)
async def setup_test_db(db_engine, db_session_factory):
    assert db_engine.url.database == "test", "Not test DB is using, aborting!"

    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    def load_json(name: str):
        mock_dir = Path(__file__).parent / "mock"
        with open(mock_dir / f"{name}.json", "r", encoding="utf-8") as f:
            return json.load(f)

    def filter_insertable_fields(_data: list[dict], _model) -> list[dict]:
        valid_keys = {col.name for col in _model.__table__.columns}
        return [{k: v for k, v in row.items() if k in valid_keys} for row in _data]

    mock_files = ["categories", "sub_categories", "products", "offers"]
    mocks = {name: load_json(name) for name in mock_files}

    model_map = {
        "categories": Category,
        "sub_categories": SubCategory,
        "products": Product,
        "offers": Offer,
    }

    async with db_session_factory() as session:
        for name, model in model_map.items():
            if raw_data := mocks.get(name):
                data = filter_insertable_fields(raw_data, model)
                await session.execute(insert(model).values(data))
        await session.commit()


# -------------------------------
# 🔁 Override get_db for FastAPI
# -------------------------------
@pytest.fixture(scope="session", autouse=True)
def override_app_db(db_session_factory):
    from src.__main__ import app
    from src.api.di.database import get_db

    async def override_get_db():
        async with db_session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    print("🔄 Overridden get_db dependency for FastAPI")


# -------------------------------
# 🧪 Client for HTTP testing
# -------------------------------
mock.patch("fastapi_cache.decorator.cache", lambda *args, **kwargs: lambda f: f).start()


@pytest.fixture(scope="session")
async def client(setup_test_db) -> AsyncGenerator[AsyncClient, None]:
    from src.__main__ import app

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
        headers={"Content-Type": "application/json"},
    ) as test_client:
        yield test_client
