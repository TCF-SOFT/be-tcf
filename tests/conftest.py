import json
from pathlib import Path
from typing import AsyncGenerator
from unittest import mock

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import insert
from src.common.services.s3_service import S3Service
from src.config import settings
from src.models import Category, Offer, Product, SubCategory
from src.models.base import Base
from src.utils.logging import logger


@pytest.fixture(scope="function")
async def patch_db(monkeypatch):
    from src.api.di.db_helper import DatabaseHelper

    test_helper = DatabaseHelper(settings.DB.PSQL_URL, is_test=True)
    logger.warning(settings.DB.PSQL_URL)
    monkeypatch.setattr("src.api.di.db_helper.db_helper", test_helper)
    yield
    await test_helper.dispose()


# -------------------------------
# DB Schema Setup & Seeding
# -------------------------------
@pytest.fixture(scope="function", autouse=True)
async def setup_test_db(patch_db):
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


@pytest.fixture(scope="function")
async def client() -> AsyncGenerator[AsyncClient, None]:
    from src.__main__ import app

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
        headers={"Content-Type": "application/json"},
    ) as test_client:
        # app.state.resources = ResourceModule(redis_service=RedisService())
        # app.state.redis_service = app.state.resources.get_redis_service()
        # app.state.redis = app.state.redis_service.get_redis()
        app.state.s3 = S3Service(
            access_key=settings.AWS.S3_ACCESS_KEY,
            secret_key=settings.AWS.S3_SECRET_KEY,
            region=settings.AWS.S3_DEFAULT_REGION,
            endpoint=settings.AWS.S3_ENDPOINT_URL,
            bucket=settings.AWS.S3_BUCKET_NAME,
        )
        yield test_client


# TODO: restrict registration under the Employee role
@pytest.fixture
async def employee_token(client: AsyncClient) -> str:
    await client.post(
        "/auth/register",
        json={
            "email": "employee@test.com",
            "password": "test",
            "first_name": "Test",
            "role": "EMPLOYEE",
            "is_active": True,  # после регистрации
            "is_superuser": False,  # только админ
            "is_verified": False,  # после подтверждения
        },
    )

    res = await client.post(
        "/auth/login",
        data={
            "grant_type": "password",
            "username": "employee@test.com",
            "password": "test",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    logger.warning(res.text)
    assert res.status_code == 200, "Login failed"
    return res.json()["access_token"]


@pytest.fixture
async def auth_client(client: AsyncClient, employee_token: str) -> AsyncClient:
    client.headers["Authorization"] = f"Bearer {employee_token}"
    return client
