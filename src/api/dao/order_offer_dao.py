from sqlalchemy.exc import SQLAlchemyError

from src.api.dao.base import BaseDAO
from src.models import OrderOffer
from src.utils.logging import logger


class OrderOfferDAO(BaseDAO):
    model = OrderOffer

    @classmethod
    async def add(cls, db_session, **values) -> OrderOffer:
        """
        More: https://habr.com/ru/articles/828328/, 'Управление транзакциями'
        :param db_session:
        :param values:
        :return:
        """
        try:
            new_instance = cls.model(**values)
            db_session.add(new_instance)
            await db_session.flush()  # Ensure the instance is added to the session
            await db_session.commit()
            return new_instance

        except SQLAlchemyError as e:
            logger.error("SQLAlchemyError: %s", e)
            raise e
