from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from api.dao.base import BaseDAO
from models.models import Product


class ProductDAO(BaseDAO):
    model = Product

    @classmethod
    async def find_all(cls, db_session, filter_by: dict, count: bool = False):
        query = select(cls.model).filter_by(**filter_by)
        return await paginate(db_session, query)
