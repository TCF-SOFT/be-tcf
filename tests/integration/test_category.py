from httpx import AsyncClient


class TestCategoryRoutes:
    ENDPOINT = "/categories"

    async def test_get_all_returns_200(self, client: AsyncClient):
        res = await client.get(self.ENDPOINT)
        assert res.status_code == 200

    async def test_get_by_slug_returns_category(self, client: AsyncClient):
        slug = "svechi"
        res = await client.get(f"{self.ENDPOINT}/slug/{slug}")
        assert res.status_code == 200
        assert isinstance(res.json(), dict), "Response body is not valid"
        assert "id" in res.json(), "ID is not present in response body"

    async def test_get_by_id_returns_404_if_missing(self, client: AsyncClient):
        category_id = "980940df-9615-42dd-b72a-8779ae508efa"
        res = await client.get(f"{self.ENDPOINT}/{category_id}")
        assert res.status_code == 404

    async def test_get_by_invalid_id_returns_422(self, client: AsyncClient):
        category_id = "invalid-id"
        res = await client.get(f"{self.ENDPOINT}/{category_id}")
        assert res.status_code == 422, "Expected 422 for invalid ID format"

    async def test_post_category_creates_category(self, client: AsyncClient):
        pass

    async def test_patch_category_updates_existing(self, client: AsyncClient):
        pass

    async def test_delete_category_deletes_and_returns_204(self, client: AsyncClient):
        pass
