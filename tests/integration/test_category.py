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
        pass

    async def test_post_category_creates_category(self, client: AsyncClient):
        pass

    async def test_patch_category_updates_existing(self, client: AsyncClient):
        pass

    async def test_delete_category_deletes_and_returns_204(self, client: AsyncClient):
        pass
