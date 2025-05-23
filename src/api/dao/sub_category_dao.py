from sqlalchemy import select

from api.dao.base import BaseDAO
from models.models import SubCategory


class SubCategoryDAO(BaseDAO):
    model = SubCategory

    @classmethod
    async def find_by_slug(cls, db_session, slug: str):
        """
        Find a category by its slug.
        """
        query = select(cls.model).filter_by(slug=slug)
        result = await db_session.execute(query)
        res = result.scalar_one_or_none()
        return res
