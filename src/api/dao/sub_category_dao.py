from sqlalchemy import select

from src.api.dao.base import BaseDAO
from src.models import SubCategory


class SubCategoryDAO(BaseDAO):
    model = SubCategory

    @classmethod
    async def find_by_slug(cls, db_session, slug: str) -> SubCategory | None:
        """
        Find a SubCategory by its slug.
        """
        query = select(cls.model).filter_by(slug=slug)
        result = await db_session.execute(query)
        res = result.scalar_one_or_none()
        return res
