import json
from pathlib import Path

from httpx import AsyncClient

from src.utils.logging import logger


class TestCategoryRoutes:
    ENDPOINT = "/categories"
    mock_dir = Path(__file__).parent.parent / "mock"

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


    async def test_unauthorized_post_category_returns_401(self, client: AsyncClient):
        payload = {
            "name": "candles test category",
        }
        image = {
            "image_blob": open(self.mock_dir / "candles.webp", "rb"),
        }
        res = await client.post(self.ENDPOINT, data=payload, files=image)
        assert res.status_code == 401, "Expected 401 Unauthorized for unauthenticated request"


    async def test_post_category_creates_category(self, auth_client: AsyncClient):
        pass
        # TODO: разобраться с form-data, multipart и тд + Фронт
        # data = {
        #     "name": "candles test category"  # <- это поле Form(...)
        # }
        # files = {
        #     "image_blob": (
        #         "candles.webp",
        #         open(self.mock_dir / "candles.webp", "rb"),
        #         "image/webp",
        #     )
        # }
        #
        # res = await auth_client.post("/categories", data=data, files=files)
        # logger.warning("[POST] Category response: %s", res.text)
        # assert res.status_code == 201
        #
        # response = res.json()
        #
        # assert isinstance(response, dict), "Response body is not valid"
        # assert "id" in response, "ID is not present in response body"
        # assert "slug" in response, "Slug is not present in response body"
        # assert "image" in response, "Image is not present in response body"

    async def test_patch_category_updates_existing(self, client: AsyncClient):
        pass

    async def test_delete_category_deletes_and_returns_204(self, client: AsyncClient):
        pass
