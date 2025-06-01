from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from src.api.dao.base import BaseDAO
from src.models.models import WaybillOffer


class WaybillOfferDAO(BaseDAO):
    model = WaybillOffer

    @classmethod
    async def find_one_or_none(cls, db_session, filter_by: dict) -> list or None:
        query = select(cls.model).filter_by(**filter_by)
        result = await db_session.execute(query)
        return result.unique().scalar_one_or_none()

    @classmethod
    async def add(cls, db_session, **values) -> WaybillOffer:
        """
        More: https://habr.com/ru/articles/828328/, 'Управление транзакциями'
        :param db_session:
        :param values:
        :return:
        """
        try:
            new_instance = cls.model(**values)
            db_session.add(new_instance)
            return new_instance

        except SQLAlchemyError as e:
            raise e
