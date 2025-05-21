from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from api.dao.base import BaseDAO
from common.exceptions.exceptions import DuplicateSlugError
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

    @classmethod
    async def add(cls, db_session: AsyncSession, **values) -> SubCategory:
        """
        Insert one SubCategory row and return the ORM instance.
        `values` may include category_id, category_slug, slug, image_url, etc.
        """
        try:
            async with db_session.begin():  # ← commit on exit
                obj = cls.model(**values)
                db_session.add(obj)

            await db_session.refresh(obj)  # ← populate PK, defaults
            return obj

        except IntegrityError as e:
            slug_value = values.get("slug", "N/A")
            raise DuplicateSlugError(slug=slug_value) from e

        except SQLAlchemyError as e:
            raise e
