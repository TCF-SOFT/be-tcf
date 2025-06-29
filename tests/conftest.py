import asyncio
import json
from pathlib import Path
from typing import AsyncGenerator
from unittest import mock

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import insert
# from src.__main__ import app
from src.api.di.db_helper import DatabaseHelper
from src.models import Category, Offer, Product, SubCategory
from src.models.base import Base
# from testcontainers.localstack import LocalStackContainer
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

# from common.services.s3_service import S3Service
from config import settings


# @pytest.fixture(scope="session")
# def localstack_container():
#     with LocalStackContainer(image="localstack/localstack:4.4.0").with_services(
#         "s3"
#     ) as localstack:
#         endpoint = localstack.get_url()
#
#         s3 = S3Service(
#             endpoint=endpoint,
#             access_key="test",
#             secret_key="test",
#             region="eu-north-1",
#             bucket="test-bucket",
#         )
#
#     app.state.s3 = s3
#
#     # создаём бакет в localstack
#     import asyncio
#
#     async def create_bucket():
#         async with s3._client() as client:
#             await client.create_bucket(
#                 Bucket=s3._bucket,
#                 CreateBucketConfiguration={
#                     "LocationConstraint": localstack.region_name
#                 },
#             )
#
#     asyncio.get_event_loop().run_until_complete(create_bucket())
#
#     yield


# -------------------------------
# 🔌 Database & Redis containers
# -------------------------------
@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer(
        image="postgres:17",
        username=settings.DB.PSQL_USER,
        password=settings.DB.PSQL_PASS,
        dbname=settings.DB.PSQL_DB,
        port=settings.DB.PSQL_PORT,
    ).with_bind_ports(settings.DB.PSQL_PORT, settings.DB.PSQL_PORT) as postgres:
        # sleep(600)
        yield postgres


@pytest.fixture(scope="session")
def redis_container():
    with RedisContainer("redis:7") as redis:
        yield redis


@pytest.fixture(scope="session", autouse=True)
def patch_db_helper(postgres_container):
    # 1. строим URL контейнера
    url = postgres_container.get_connection_url(driver="asyncpg")

    # 2. создаём новый helper, указывая is_test=True (NullPool и т.д.)
    test_helper = DatabaseHelper(url, is_test=True)

    # 3. подменяем глобальную переменную *в самом модуле* db_helper
    import importlib

    helper_module = importlib.import_module("src.api.di.db_helper")
    helper_module.db_helper = test_helper  # <-- ключевая строка

    yield

    # 4. аккуратно закрываем в конце сессии
    asyncio.get_event_loop().run_until_complete(test_helper.dispose())


# -------------------------------
# DB Schema Setup & Seeding
# -------------------------------
@pytest.fixture(scope="session", autouse=True)
async def setup_test_db(patch_db_helper):
    from src.api.di.db_helper import db_helper

    # safety check
    assert "test" in str(db_helper.engine.url), "Using non-test DB!"

    async with db_helper.engine.begin() as conn:
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

    async with db_helper.AsyncSessionFactory() as session:
        for name, model in model_map.items():
            if raw_data := mocks.get(name):
                data = filter_insertable_fields(raw_data, model)
                await session.execute(insert(model).values(data))
        await session.commit()


# -------------------------------
# 🧪 Client for HTTP testing
# -------------------------------
mock.patch("fastapi_cache.decorator.cache", lambda *args, **kwargs: lambda f: f).start()


@pytest.fixture(scope="session")
async def client(
    setup_test_db, localstack_container
) -> AsyncGenerator[AsyncClient, None]:
    from src.__main__ import app

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
        headers={"Content-Type": "application/json"},
    ) as test_client:
        yield test_client
