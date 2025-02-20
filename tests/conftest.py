import pytest
from httpx import ASGITransport, AsyncClient

from api.di.di import ResourceModule
from api.di.redis_service import RedisService


@pytest.fixture(
    scope="session",
    params=[
        pytest.param(("asyncio", {"use_uvloop": True}), id="asyncio+uvloop"),
    ],
)
def anyio_backend(request):
    return request.param


@pytest.fixture(scope="session")
async def client() -> AsyncClient:
    # need to load app module after mock. otherwise, it would fail
    from src.__main__ import app

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
        headers={"Content-Type": "application/json"},
    ) as test_client:
        app.state.resources = ResourceModule(redis=RedisService())
        yield test_client
