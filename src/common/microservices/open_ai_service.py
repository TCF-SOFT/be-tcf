# import logging
#
# from openai import AsyncOpenAI
# from tenacity import (
#     after_log,
#     retry,
#     stop_after_attempt,
#     wait_exponential,
# )
#
# from src.config import settings
# from src.utils.logging import logger
#
# client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
#
#
# @retry(
#     stop=stop_after_attempt(3),
#     wait=wait_exponential(multiplier=1, min=2, max=6),
#     after=(after_log(logger, logging.ERROR)),
# )
# async def get_embedding(text: str) -> list[float] | None:
#     """
#     Получить векторное представление текста с помощью OpenAI API.
#
#     :param text: Текст для преобразования в вектор.
#     :return: Векторное представление текста.
#     """
#     try:
#         response = await client.embeddings.create(
#             input=text, model="text-embedding-3-small"
#         )
#         return response.data[0].embedding
#     except Exception as e:
#         logger.error(f"OpenAI embedding error: {e}")
#         return None
