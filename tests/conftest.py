import base64
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import AsyncGenerator
from unittest import mock

import jwt
import pytest
from asgi_lifespan import LifespanManager
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from httpx import ASGITransport, AsyncClient
from sqlalchemy import insert
from src.common.services.s3_service import S3Service
from src.config import settings
from src.models import Category, Offer, Product, SubCategory, User
from src.models.base import Base


@pytest.fixture(scope="function")
async def patch_db(monkeypatch):
    from src.api.di.db_helper import DatabaseHelper

    test_helper = DatabaseHelper(settings.DB.PSQL_URL, is_test=True)
    # logger.warning(settings.DB.PSQL_URL)
    monkeypatch.setattr("src.api.di.db_helper.db_helper", test_helper)
    yield
    await test_helper.dispose()


# Один и тот же ключ — на весь тестовый ран
TEST_PRIVATE_KEY = Ed25519PrivateKey.generate()
TEST_PUBLIC_KEY = TEST_PRIVATE_KEY.public_key()


def base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


@pytest.fixture(autouse=True)
def mock_jwks(monkeypatch):
    x = base64url_encode(
        TEST_PUBLIC_KEY.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
    )

    keys = [
        {
            "kty": "OKP",
            "crv": "Ed25519",
            "alg": "EdDSA",
            "kid": "test-key",
            "x": x,
        }
    ]

    # sync-функция, а не async
    def fake_load_jwks():
        # важно: вернуть тот же тип, который возвращает реальный load_jwks
        # если у тебя в better_auth.py:
        #   return resp.json()["keys"]
        # то здесь тоже нужно вернуть список keys
        return keys

    monkeypatch.setattr(
        "src.api.auth.better_auth.load_jwks",
        fake_load_jwks,
    )


def create_test_jwt(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "email": "test@example.com",
        "iat": int(datetime.now().timestamp()),
        "exp": int((datetime.now() + timedelta(hours=1)).timestamp()),
        "iss": "http://testserver",
        "aud": "http://testserver",
        "name": "Test User",
        "first_name": "Test",
        "last_name": "User",
    }

    token = jwt.encode(
        payload,
        TEST_PRIVATE_KEY,
        algorithm="EdDSA",
        headers={"kid": "test-key"},
    )

    return token


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

    mock_files = ["categories", "sub_categories", "products", "offers", "users"]
    mocks = {name: load_json(name) for name in mock_files}

    model_map = {
        "categories": Category,
        "sub_categories": SubCategory,
        "products": Product,
        "offers": Offer,
        "users": User,
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
async def client() -> AsyncGenerator[AsyncClient, None]:
    from src.__main__ import app

    async with (
        AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://testserver",
            headers={"Content-Type": "application/json", "Origin": "http://testserver"},
        ) as test_client,
        LifespanManager(app),
    ):
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


@pytest.fixture
async def auth_client(client: AsyncClient) -> AsyncClient:
    token = create_test_jwt(user_id="afd4fafb-86b3-4280-a829-f2fcdd9c203d")
    client.headers["Authorization"] = f"Bearer {token}"
    return client
