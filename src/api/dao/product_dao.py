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
