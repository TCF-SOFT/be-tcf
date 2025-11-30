from uuid import UUID

from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dao.base import BaseDAO
from src.models import Category, Product, SubCategory
from src.schemas.product_schema import ProductSchema
from src.utils.pagination import Page


class ProductDAO(BaseDAO):
    model = Product
    schema = ProductSchema

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
        Use lexeme to search for the term in the name, description, manufacturer_number, sku and brand.

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
    async def get_product_counts_per_category(cls, db_session: AsyncSession):
        query = (
            select(Category.name, func.count(Product.id))
            .join(SubCategory, SubCategory.category_id == Category.id)
            .join(Product, Product.sub_category_id == SubCategory.id)
            .group_by(Category.name)
        )

        result = await db_session.execute(query)
        rows = result.all()
        return dict(rows)

    @classmethod
    async def get_product_counts_per_sub_category(
        cls,
        db_session: AsyncSession,
        category_id: UUID,
    ):
        query = (
            select(SubCategory.name, func.count(Product.id))
            .join(Category, Category.id == SubCategory.category_id)
            .join(Product, Product.sub_category_id == SubCategory.id)
            .where(Category.id == category_id)
            .group_by(SubCategory.name)
        )

        result = await db_session.execute(query)
        rows = result.all()
        return dict(rows)
