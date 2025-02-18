from httpx import AsyncClient


class TestProductsGet:
    """
    Test the GET method for the products endpoint
    """

    CONTROLLER_ENDPOINT = "/cocktails"
    OLD_FASHIONED_ID = "d1f1e7e9-4c7a-4e8b-9d7f-1e3f6a4c5b7c"
    COSMOPOLITAN_ID = "f9a7e6b3-4e9c-4c6e-9b8d-3e4f6c7e2a5d"  # missing in stock

    async def test_get_products(self, client: AsyncClient):
        response = await client.get(self.CONTROLLER_ENDPOINT)
        assert response.status_code == 200
        assert response.json()["items"] is not None
        assert len(response.json()["items"]) > 0

    async def test_get_products_pagination(self, client: AsyncClient):
        response = await client.get(f"{self.CONTROLLER_ENDPOINT}?page=1&size=2")
        first_drink = response.json()["items"][0]
        assert response.json()["total"] > 0
        assert response.json()["page"] == 1
        assert response.json()["size"] == 2
        assert response.json()["pages"] > 0

        response = await client.get(f"{self.CONTROLLER_ENDPOINT}?page=2&size=2")
        third_drink = response.json()["items"][0]
        assert response.json()["page"] == 2
        assert response.json()["size"] == 2
        assert response.json()["pages"] > 0
        assert first_drink != third_drink

    async def test_get_products_by_id(self, client: AsyncClient):
        response = await client.get(
            f"{self.CONTROLLER_ENDPOINT}", params={"cocktail_id": self.OLD_FASHIONED_ID}
        )
        assert response.status_code == 200
        assert response.json()["items"][0]["id"] == self.OLD_FASHIONED_ID

    async def test_missing_in_stock_product(self, client: AsyncClient):
        response = await client.get(
            f"{self.CONTROLLER_ENDPOINT}", params={"cocktail_id": self.COSMOPOLITAN_ID}
        )
        assert response.status_code == 200
        assert len(response.json()["items"]) == 0

        response = await client.get(
            f"{self.CONTROLLER_ENDPOINT}",
            params={"cocktail_id": self.COSMOPOLITAN_ID, "in_stock": False},
        )
        assert response.status_code == 200
        assert len(response.json()["items"]) == 1

    async def test_get_products_with_labels(self, client: AsyncClient):
        response = await client.get(
            f"{self.CONTROLLER_ENDPOINT}", params={"labels": ["Classic"]}
        )
        assert response.status_code == 200
        assert len(response.json()["items"]) > 0
        for item in response.json()["items"]:
            assert item["labels"][0]["name"] == "Classic"

    # async def test_order_by(self, client: AsyncClient):
    #     response = await client.get(f"{self.CONTROLLER_ENDPOINT}", params={
    #         "order_by": "alcohol_content"
    #     })
    #     assert response.status_code == 200
    #     assert len(response.json()['items']) > 0
    #     prev_alcohol_content = 0
    #     for item in response.json()['items']:
    #         assert prev_alcohol_content <= item['alcohol_content']
    #         prev_alcohol_content = item['alcohol_content']


class TestFuzzySearch:
    pass


class TestProductsPost:
    """
    Test the POST method for the products endpoint
    """

    CONTROLLER_ENDPOINT = "/cocktail"

    async def test_post_product_with_labels(self, client: AsyncClient):
        response = await client.post(
            self.CONTROLLER_ENDPOINT,
            json={
                "name": "Dark and Stormy",
                "description": "A cocktail made with dark rum and ginger beer",
                "recipe": "Mix dark rum and ginger beer in a glass with ice",
                "alcohol_content": 10.0,
                "in_stock": True,
                "labels": [{"name": "Classic"}],
            },
        )
        assert response.status_code == 201
        assert response.json()["name"] == "Dark and Stormy"

        created_drink_id = response.json()["id"]
        assert created_drink_id is not None

        assert "labels" in response.json()
        assert "images" in response.json()

        assert response.json()["labels"][0]["name"] == "Classic"
        assert response.json()["images"] == []

    async def test_post_product_with_images(self, client: AsyncClient):
        response = await client.post(
            self.CONTROLLER_ENDPOINT,
            json={
                "name": "Test cocktail",
                "description": "Test description",
                "recipe": "Test recipe",
                "alcohol_content": 10.0,
                "in_stock": True,
                "images": [{"image_url": "https://test.com/test.jpg"}],
            },
        )
        assert response.status_code == 201
        assert response.json()["name"] == "Test cocktail"
        assert response.json()["images"][0]["image_url"] == "https://test.com/test.jpg"


class TestProductsPut:
    """
    Test the PUT method for the products endpoint
    """

    CONTROLLER_ENDPOINT = "/cocktails"
    OLD_FASHIONED_ID = "d1f1e7e9-4c7a-4e8b-9d7f-1e3f6a4c5b7c"
    COSMOPOLITAN_ID = "f9a7e6b3-4e9c-4c6e-9b8d-3e4f6c7e2a5d"

    async def test_update_product(self, client: AsyncClient):
        response = await client.put(
            f"{self.CONTROLLER_ENDPOINT}/{self.OLD_FASHIONED_ID}",
            json={
                "name": "New Old Fashioned",
                "description": "New description",
                "recipe": "New recipe",
                "alcohol_content": 0.0,
                "in_stock": True,
            },
        )
        assert response.status_code == 200
        assert response.json()["name"] == "New Old Fashioned"
        assert response.json()["description"] == "New description"
        assert response.json()["recipe"] == "New recipe"
        assert response.json()["alcohol_content"] == 0.0

    async def test_update_product_with_images(self, client: AsyncClient):
        response = await client.put(
            f"{self.CONTROLLER_ENDPOINT}/{self.OLD_FASHIONED_ID}",
            json={
                "name": "Old Fashioned",
                "description": "A classic cocktail made with bourbon, sugar, and bitters",
                "recipe": "Mix bourbon, sugar, and bitters in a glass with ice",
                "alcohol_content": 10.0,
                "in_stock": True,
                "images": [{"image_url": "https://test.com/test.jpg"}],
            },
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Old Fashioned"
        assert response.json()["images"][0]["image_url"] == "https://test.com/test.jpg"

    async def test_update_product_with_empty_images(self, client: AsyncClient):
        response = await client.put(
            f"{self.CONTROLLER_ENDPOINT}/{self.OLD_FASHIONED_ID}",
            json={
                "name": "Old Fashioned",
                "description": "A classic cocktail made with bourbon, sugar, and bitters",
                "recipe": "Mix bourbon, sugar, and bitters in a glass with ice",
                "alcohol_content": 10.0,
                "in_stock": True,
                "images": [],
            },
        )
        assert response.status_code == 200
        assert response.json()["images"] == []

    async def test_update_product_with_labels(self, client: AsyncClient):
        response = await client.put(
            f"{self.CONTROLLER_ENDPOINT}/{self.OLD_FASHIONED_ID}",
            json={
                "name": "Old Fashioned",
                "description": "A classic cocktail made with bourbon, sugar, and bitters",
                "recipe": "Mix bourbon, sugar, and bitters in a glass with ice",
                "alcohol_content": 10.0,
                "in_stock": True,
                "labels": [{"name": "Spicy"}, {"name": "Classic"}],
            },
        )
        assert response.status_code == 200
        assert len(response.json()["labels"]) == 2

    async def test_update_product_with_invalid_label(self, client: AsyncClient):
        await client.put(
            f"{self.CONTROLLER_ENDPOINT}/{self.OLD_FASHIONED_ID}",
            json={
                "name": "Old Fashioned",
                "description": "A classic cocktail made with bourbon, sugar, and bitters",
                "recipe": "Mix bourbon, sugar, and bitters in a glass with ice",
                "alcohol_content": 10.0,
                "in_stock": True,
                "labels": [
                    {"name": "TEST_LABEL"},
                ],
            },
        )
        # TODO: use only prepared list of labels
        # assert response.status_code == 400

    async def test_update_product_with_empty_labels(self, client: AsyncClient):
        response = await client.put(
            f"{self.CONTROLLER_ENDPOINT}/{self.OLD_FASHIONED_ID}",
            json={
                "name": "Old Fashioned",
                "description": "A classic cocktail made with bourbon, sugar, and bitters",
                "recipe": "Mix bourbon, sugar, and bitters in a glass with ice",
                "alcohol_content": 10.0,
                "in_stock": True,
                "labels": [],
            },
        )
        assert response.status_code == 200
        assert response.json()["labels"] == []


class TestProductsDelete:
    pass
