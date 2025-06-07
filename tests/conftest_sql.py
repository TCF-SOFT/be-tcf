import json
import os
from unittest import mock

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import async_sessionmaker
from src.api.di.database import engine
from src.config.config import settings
from src.models.base import Base
from src.models.models import Cocktail, CocktailLabel, Image, Label, Rating, User

from common.services.redis_service import get_redis

os.environ["MODE"] = "TEST"

SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


@pytest.fixture(
    scope="session",
    params=[
        pytest.param(("asyncio", {"use_uvloop": True}), id="asyncio+uvloop"),
    ],
)
def anyio_backend(request):
    return request.param


# autouse=True: automatically use this fixture for all tests
@pytest.fixture(scope="session", autouse=True)
async def start_db():
    # check if database is a test database to avoid accidental deletion
    assert engine.url.database == settings.TEST_PSQL_DB
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    def open_mock_json(model: str):
        with open(f"tests/mock_data/{model}.json", "r", encoding="utf-8") as file:
            return json.load(file)

    cocktails = open_mock_json("cocktails")
    labels = open_mock_json("labels")
    cocktail_labels = open_mock_json("cocktail_labels")
    images = open_mock_json("images")
    users = open_mock_json("users")
    # orders = open_mock_json("orders")
    # order_cocktails = open_mock_json("order_cocktails")
    ratings = open_mock_json("ratings")
    # carts = open_mock_json("carts")
    # cart_items = open_mock_json("cart_items")

    async with SessionLocal() as session:
        add_labels = insert(Label).values(labels)
        await session.execute(add_labels)

        add_cocktails = insert(Cocktail).values(cocktails)
        await session.execute(add_cocktails)

        add_images = insert(Image).values(images)
        await session.execute(add_images)

        add_users = insert(User).values(users)
        await session.execute(add_users)

        # add_carts = insert(Cart).values(carts)
        # await session.execute(add_carts)

        # add_cart_items = insert(CartItem).values(cart_items)
        # await session.execute(add_cart_items)

        # add_orders = insert(Order).values(orders)
        # await session.execute(add_orders)

        # add_order_cocktails = insert(OrderCocktail).values(order_cocktails)
        # await session.execute(add_order_cocktails)

        add_cocktail_labels = insert(CocktailLabel).values(cocktail_labels)
        await session.execute(add_cocktail_labels)

        add_ratings = insert(Rating).values(ratings)
        await session.execute(add_ratings)

        await session.commit()

    # for AsyncEngine created in function scope, close and
    # clean-up pooled connections
    await engine.dispose()


# Solve cache problem: https://github.com/long2ice/fastapi-cache/issues/49
mock.patch("fastapi_cache.decorator.cache", lambda *args, **kwargs: lambda f: f).start()


@pytest.fixture(scope="session")
async def client(start_db) -> AsyncClient:
    # need to load app module after mock. otherwise, it would fail
    from src.__main__ import app

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
        headers={"Content-Type": "application/json"},
    ) as test_client:
        app.state.redis = await get_redis()
        yield test_client
