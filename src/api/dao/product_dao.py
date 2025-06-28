from uuid import UUID

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import func, or_, select

from api.dao.base import BaseDAO
from common.microservices.open_ai_service import get_embedding
from schemas.product_schema import ProductSchema
from src.models import Product


class ProductDAO(BaseDAO):
    model = Product

    @classmethod
    async def find_all_paginate(
        cls, db_session, filter_by: dict
    ) -> Page[ProductSchema]:
        query = select(cls.model).filter_by(**filter_by)
        return await paginate(db_session, query)

    @classmethod
    async def find_by_id(cls, db_session, _id: UUID) -> ProductSchema:
        """
        Базовый метод DAO должен проходить через model_validate()
         для преобразования в нужную схему с последующей сериализацией.
        """
        query = select(cls.model).filter_by(id=_id)
        result = await db_session.execute(query)
        res = result.scalar_one_or_none()
        return ProductSchema.model_validate(res)

    @classmethod
    async def wildcard_search(
        cls,
        db_session,
        search_term: str,
    ) -> Page[ProductSchema]:
        search_term = f"%{search_term.replace('.', '')}%"

        query = select(cls.model).where(
            or_(
                func.replace(cls.model.name, ".", "").ilike(search_term),
                func.replace(cls.model.cross_number, ".", "").ilike(search_term),
                func.replace(cls.model.address_id, ".", "").ilike(search_term),
            )
        )

        return await paginate(db_session, query)

    @classmethod
    async def full_text_search(
        cls,
        db_session,
        search_term: str,
    ) -> Page[ProductSchema]:
        """
        Perform a full-text search on the product.
        Use lexeme to search for the term in the name, description, manufacturer_number, address_id and brand.

        article: https://habr.com/ru/companies/beeline_cloud/articles/742214/

        Триграмма — это группа трёх последовательных символов, взятых из строки.
        Мы можем измерить схожесть двух строк, подсчитав число триграмм, которые есть в обеих.
        Эта простая идея оказывается очень эффективной для измерения схожести слов на многих естественных языках.
        """
        query = (
            select(cls.model)
            .where(func.similarity(cls.model.name, search_term) > 0.1)
            .order_by(func.similarity(cls.model.name, search_term).desc())
        )
        return await paginate(db_session, query)

    @classmethod
    async def vector_search(
        cls,
        db_session,
        search_term: str,
    ) -> Page[ProductSchema]:
        """
        Perform a vector search on the product.
        Show the most similar products to the search term.

        library: https://github.com/pgvector/pgvector-python?tab=readme-ov-file#sqlalchemy
        """
        # TODO:
        # - использование собственного векторизатора (размер векторов)
        # - автоматическое обновление векторов при изменении товара
        # - install extension pgvector в postgres при тестах

        # 1. Получить embedding поискового запроса
        query_vector: list[float] = await get_embedding(search_term)

        # 2. order_by method - all results (vol. 1)
        # query = (
        #     select(cls.model).order_by(cls.model.embedding.l2_distance(query_vector))
        #     .limit(100)
        # )
        # filter method - limited (vol. 2)
        query = (
            select(cls.model)
            .filter(cls.model.embedding.l2_distance(query_vector) < 1.1)
            .order_by(cls.model.embedding.l2_distance(query_vector))
        )

        return await paginate(db_session, query)
