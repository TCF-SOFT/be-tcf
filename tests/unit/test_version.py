from httpx import AsyncClient


class TestVersion:
    async def test_version(self, client: AsyncClient):
        response = await client.get("/-/version")
        assert response.status_code == 200

        response = response.json()
        assert response["version"] is not None, "No version was returned"
