from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from api.dao.base import BaseDAO
from models.models import Category


class CategoryDAO(BaseDAO):
    model = Category

    @classmethod
    async def find_by_slug(cls, db_session, slug: str):
        """
        Find a category by its slug.
        """
        query = select(cls.model).filter_by(slug=slug)
        result = await db_session.execute(query)
        res = result.scalar_one_or_none()
        return res

    @classmethod
    async def add(cls, db_session: AsyncSession, **values) -> Category:
        """
        Insert one Category row and return the ORM instance.
        `values` may include slug, image_url, etc.
        """
        try:
            async with db_session.begin():  # ← commit on exit
                obj = cls.model(**values)
                db_session.add(obj)

            await db_session.refresh(obj)  # ← populate PK, defaults
            return obj

        except SQLAlchemyError:
            # `begin()` already rolled back; simply propagate for your 500 handler
            raise
