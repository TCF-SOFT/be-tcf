from uuid import UUID

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import func, or_, select

from api.dao.base import BaseDAO
from models.models import Offer
from schemas.offer_schema import OfferSchema


class OfferDAO(BaseDAO):
    model = Offer

    @classmethod
    async def find_all(
        cls, db_session, filter_by: dict, count: bool = False, order_by: str = None
    ) -> Page[OfferSchema]:
        query = select(cls.model).filter_by(**filter_by)
        return await paginate(db_session, query)

    @classmethod
    async def find_by_id(cls, db_session, _id: UUID) -> OfferSchema:
        """
        Базовый метод DAO должен проходить через model_validate()
         для преобразования в нужную схему с последующей сериализацией.
        """
        query = select(cls.model).filter_by(id=_id)
        result = await db_session.execute(query)
        res = result.scalar_one_or_none()
        return OfferSchema.model_validate(res)

    @classmethod
    async def wildcard_search(
        cls,
        db_session,
        search_term: str,
    ) -> Page[OfferSchema]:
        search_term = f"%{search_term.replace('.', '')}%"

        query = select(cls.model).where(
            or_(
                func.replace(cls.model.brand, ".", "").ilike(search_term),
                func.replace(cls.model.manufacturer_number, ".", "").ilike(search_term),
            )
        )

        return await paginate(db_session, query)
