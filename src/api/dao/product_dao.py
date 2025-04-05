from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select, func, or_

from api.dao.base import BaseDAO
from models.models import Product
from schemas.schemas import ProductSchema


class ProductDAO(BaseDAO):
    model = Product

    @classmethod
    async def find_all(cls, db_session, filter_by: dict, count: bool = False):
        query = select(cls.model).filter_by(**filter_by)
        return await paginate(db_session, query)

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
                func.replace(cls.model.manufacturer_number, ".", "").ilike(search_term),
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
        query = select(cls.model).where(
            func.similarity(
                cls.model.name, search_term
            ) > 0.1
        ).order_by(
            func.similarity(cls.model.name, search_term).desc()
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
        pass
