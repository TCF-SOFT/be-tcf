import httpx

from src.utils.singleton import SingletonMeta


class ElasticSearchHTTP(metaclass=SingletonMeta):
    def __init__(self, url: str, api_key: str):
        self.url = url
        self.api_key = api_key
        self.headers: dict = {"api_key": api_key}

    async def get_cluster_info(self):
        async with httpx.AsyncClient() as client:
            res = client.get(self.url, headers=self.headers)
            return res

    async def full_text_search(self, query: str):
        async with httpx.AsyncClient() as client:
            res = client.post(self.url, headers=self.headers, json=query)
            return res
