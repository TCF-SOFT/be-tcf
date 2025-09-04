from httpx import AsyncClient


class TestHealthCheck:
    async def test_health_check(self, client: AsyncClient):
        response = await client.get("/-/health-checks/liveness")
        assert response.status_code == 204

    async def test_health_check_readiness(self, client: AsyncClient):
        response = await client.get("/-/health-checks/readiness")
        assert response.status_code == 204
