from pathlib import Path

from httpx import AsyncClient
from src.utils.logging import logger


class TestSubCategoryRoutes:
    ENDPOINT = "/sub-categories"
    mock_dir = Path(__file__).parent.parent / "mock"

    with open(mock_dir / "candles.webp", "rb") as f:
        image_blob: bytes = f.read()

    async def test_get_all_returns_200(self, client: AsyncClient):
        res = await client.get(self.ENDPOINT)
        logger.warning("[GET] SubCategory response: %s", res.text)
        assert res.status_code == 200

    async def test_get_by_slug_returns_sub_category(self, client: AsyncClient):
        slug = "svechi-nakala"
        res = await client.get(f"{self.ENDPOINT}/slug/{slug}")
        assert res.status_code == 200

    async def test_get_by_category_slug_returns_sub_category(self, client: AsyncClient):
        category_slug = "svechi"
        res = await client.get(f"{self.ENDPOINT}?category_slug={category_slug}")
        assert res.status_code == 200

    async def test_get_by_category_slug_returns_404_if_missing(
        self, client: AsyncClient
    ):
        category_slug = "svechi-dummy-slug"
        res = await client.get(f"{self.ENDPOINT}?category_slug={category_slug}")
        assert res.status_code == 404

    async def test_get_by_category_id_returns_sub_category(self, client: AsyncClient):
        category_id = "2b3fb1a9-f13b-430f-a78e-94041fb0ed44"
        res = await client.get(f"{self.ENDPOINT}?category_id={category_id}")
        assert res.status_code == 200

    async def test_get_by_category_id_returns_404_if_missing(self, client: AsyncClient):
        category_id = "5b3fb1a9-f13b-430f-a78e-94041fb0ed40"
        res = await client.get(f"{self.ENDPOINT}?category_id={category_id}")
        assert res.status_code == 200

    async def test_get_by_id_returns_sub_category(self, client: AsyncClient):
        sub_category_id = "c9ce04fe-ed38-4006-8e5d-629d8503a90a"
        res = await client.get(f"{self.ENDPOINT}/{sub_category_id}")
        assert res.status_code == 200

    async def test_get_by_id_returns_404_if_missing(self, client: AsyncClient):
        sub_category_id = "980940df-9615-42dd-b72a-8779ae508efa"
        res = await client.get(f"{self.ENDPOINT}/{sub_category_id}")
        assert res.status_code == 404

    async def test_get_by_invalid_id_returns_422(self, client: AsyncClient):
        sub_category_id = "invalid-id"
        res = await client.get(f"{self.ENDPOINT}/{sub_category_id}")
        assert res.status_code == 422, "Expected 422 for invalid ID format"

    async def test_unauthorized_post_sub_category_returns_401(
        self, client: AsyncClient
    ):
        payload = {
            "name": "sparking candles",
        }
        image = {
            "image_blob": self.image_blob,
        }
        res = await client.post(self.ENDPOINT, data=payload, files=image)
        assert res.status_code == 401, (
            "Expected 401 Unauthorized for unauthenticated request"
        )

    async def test_post_category_creates_sub_category(self, auth_client: AsyncClient):
        auth_client.headers.pop("Content-Type", None)
        files = {
            "image_blob": (
                "candles.webp",
                self.image_blob,
                "image/webp",
            ),
            "name": (None, "sparking candles", "text/plain"),
            "category_id": (None, "2b3fb1a9-f13b-430f-a78e-94041fb0ed44", "text/plain"),
        }

        res = await auth_client.post(self.ENDPOINT, files=files)
        logger.warning("[POST] SubCategory response: %s", res.text)
        assert res.status_code == 201

        response = res.json()

        assert isinstance(response, dict), "Response body is not valid"
        assert "id" in response, "ID is not present in response body"
        assert "slug" in response, "Slug is not present in response body"
        assert "image_url" in response, "Image is not present in response body"

    async def test_unauthorized_patch_sub_category_returns_401(
        self, client: AsyncClient
    ):
        client.headers.pop("Content-Type", None)
        sub_category_id = "2b3fb1a9-f13b-430f-a78e-94041fb0ed44"
        files = {
            "image_blob": (
                "candles.webp",
                self.image_blob,
                "image/webp",
            ),
            "name": (None, "sparking candles patch", "text/plain"),
        }
        res = await client.patch(f"{self.ENDPOINT}/{sub_category_id}", files=files)
        assert res.status_code == 401, (
            "Expected 401 Unauthorized for unauthenticated request"
        )

    async def test_patch_sub_category_updates_existing(self, auth_client: AsyncClient):
        auth_client.headers.pop("Content-Type", None)
        category_id = "2b3fb1a9-f13b-430f-a78e-94041fb0ed44"
        sub_category_id = "c9ce04fe-ed38-4006-8e5d-629d8503a90a"
        new_name = "sparking candles patch"
        new_slug = "sparking-candles-patch"
        old_image_url = (
            "https://storage.yandexcloud.net/tcf-images/images/categories/candles.webp"
        )
        files = {
            "image_blob": (
                "candles.webp",
                self.image_blob,
                "image/webp",
            ),
            "name": (None, new_name, "text/plain"),
            "category_id": (None, category_id, "text/plain"),
        }
        res = await auth_client.patch(f"{self.ENDPOINT}/{sub_category_id}", files=files)
        logger.warning("[PATCH] SubCategory response: %s", res.text)
        assert res.status_code == 200

        response = res.json()

        assert isinstance(response, dict), "Response body is not valid"
        assert "id" in response, "ID is not present in response body"
        assert "slug" in response, "Slug is not present in response body"
        assert "image_url" in response, "Image is not present in response body"
        assert "category_id" in response, "Category ID is not present in response body"

        assert response["id"] == sub_category_id
        assert response["name"] == new_name
        assert response["slug"] == new_slug
        assert response["image_url"] != old_image_url
        assert response["category_id"] == category_id

    async def test_delete_sub_category_returns_404_if_missing(
        self, auth_client: AsyncClient
    ):
        sub_category_id = "c9ce04fe-ed38-4006-8e5d-629d8503a90b"
        res = await auth_client.delete(f"{self.ENDPOINT}/{sub_category_id}")
        assert res.status_code == 404, "Expected 404 for non-existing sub category"

    async def test_unauthorized_delete_sub_category_returns_401(
        self, client: AsyncClient
    ):
        sub_category_id = "c9ce04fe-ed38-4006-8e5d-629d8503a90a"
        res = await client.delete(f"{self.ENDPOINT}/{sub_category_id}")
        assert res.status_code == 401, "Expected 404 for non-existing sub category"

    async def test_delete_sub_category_deletes_and_returns_204(
        self, auth_client: AsyncClient
    ):
        sub_category_id = "c9ce04fe-ed38-4006-8e5d-629d8503a90a"
        res = await auth_client.delete(f"{self.ENDPOINT}/{sub_category_id}")
        assert res.status_code == 204, "Expected 204 for successful deletion"

        # Verify that the sub category is actually deleted
        res = await auth_client.get(f"{self.ENDPOINT}/{sub_category_id}")
        logger.warning("[GET] Deleted SubCategory response: %s", res.text)
        assert res.status_code == 404, "Expected 404 for deleted sub category"
