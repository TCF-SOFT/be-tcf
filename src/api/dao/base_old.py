from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy import update as sqlalchemy_update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from common.exceptions.exceptions import DuplicateNameError


class BaseDAO:
    """
    Создается базовый класс для всех сервисов, который содержит общие методы для всех сервисов.
    В сервисах используем нужную модель, чтобы не дублировать код.
    Унаследованные классы используем в роутерах.
    """

    model = None

    # self.model (in instance method)
    # cls.model (in classmethod)
    @classmethod
    async def find_all(
        cls, db_session, filter_by: dict, order_by: str = None
    ) -> list[model]:
        query = select(cls.model).filter_by(**filter_by).order_by(order_by)
        result = await db_session.execute(query)
        res = result.unique().scalars().all()
        return res

    @classmethod
    async def find_one_or_none(cls, db_session, filter_by: dict) -> list or None:
        query = select(cls.model).filter_by(**filter_by)
        result = await db_session.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def find_by_id(cls, db_session, _id: UUID) -> Any:
        query = select(cls.model).filter_by(id=_id)
        result = await db_session.execute(query)
        res = result.unique().scalar_one_or_none()
        return res

    @classmethod
    async def count_all(cls, db_session, filter_by: dict) -> dict[str:int]:
        """
        Count all objects in the database
        :param db_session:
        :param filter_by:
        :return:
        """
        query = select(cls.model).filter_by(**filter_by)
        result = await db_session.execute(query)
        res = result.scalars().all()
        return {"count": len(res)}

    # ---------------------------------------
    #            POST Methods
    # ---------------------------------------
    @classmethod
    async def add(cls, db_session: AsyncSession, **values) -> model:
        """
        More: https://habr.com/ru/articles/828328/, 'Управление транзакциями'
        :param db_session:
        :param values:
        :return:
        """
        try:
            new_instance = cls.model(**values)
            db_session.add(new_instance)
            await db_session.flush()
            await db_session.refresh(new_instance)
            return new_instance

        except IntegrityError as e:
            name_value = values.get("name", "N/A")
            raise DuplicateNameError(name=name_value) from e

        except SQLAlchemyError as e:
            raise e

    @classmethod
    async def add_enum(cls, db_session, model) -> Any:
        db_session.add(model)
        await db_session.commit()
        await db_session.refresh(model)
        return model

    # ---------------------------------------
    #            PUT Methods
    # ---------------------------------------
    @classmethod
    async def update(cls, db_session, filter_by: dict, **values) -> Any:
        query = (
            sqlalchemy_update(cls.model)
            .where(*[getattr(cls.model, k) == v for k, v in filter_by.items()])
            .values(**values)
            .execution_options(synchronize_db_session="fetch")
        )
        try:
            result = await db_session.execute(query)
            if result.rowcount == 0:
                return None

            select_query = select(cls.model).where(
                *[getattr(cls.model, k) == v for k, v in filter_by.items()]
            )
            res = await db_session.execute(select_query)
            return res.scalar_one_or_none()

        except IntegrityError as e:
            name_value = values.get("name", "N/A")
            raise DuplicateNameError(name=name_value) from e

        except SQLAlchemyError as e:
            raise e

    # ---------------------------------------
    #            Delete Methods
    # ---------------------------------------
    @classmethod
    async def delete_by_id(cls, db_session, _id: UUID) -> bool:
        """
        Delete an object by id
        :param db_session:
        :param _id:
        :return:
        """
        query = select(cls.model).filter_by(id=_id)
        result = await db_session.execute(query)
        enum = result.unique().scalar_one_or_none()

        if enum:
            await db_session.delete(enum)
            await db_session.commit()

            # Проверяем, что объект удален
            result = await db_session.execute(query)
            return result.scalar_one_or_none() is None

        return False
