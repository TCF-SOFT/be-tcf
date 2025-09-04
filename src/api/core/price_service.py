import io
from typing import BinaryIO

import httpx

from src.config import settings


def cast_to_binary(data: bytes) -> BinaryIO:
    return io.BytesIO(data)


async def fetch_price_list() -> BinaryIO:
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.get(f"{settings.DOCX3R_URL}/print/price")
        response.raise_for_status()
        return cast_to_binary(response.content)
