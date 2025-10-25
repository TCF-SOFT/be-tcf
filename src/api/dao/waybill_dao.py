from uuid import UUID

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.common.enums import WaybillType
from src.api.dao.base import BaseDAO
from src.models import Offer, User, Waybill
from src.schemas.waybill_schema import WaybillSchema


class WaybillDAO(BaseDAO):
    model = Waybill

    @classmethod
    async def find_all_paginate(
        cls,
        db_session,
        filter_by: dict,
        search_term: str,
    ) -> Page[WaybillSchema]:
        search_term = f"%{search_term}%"
        query = (
            select(cls.model)
            .filter_by(**filter_by)
            .where(
                or_(
                    Waybill.author.has(
                        or_(
                            User.email.ilike(search_term),
                            User.first_name.ilike(search_term),
                            User.last_name.ilike(search_term),
                            User.phone.ilike(search_term),
                        )
                    ),
                    Waybill.customer.has(
                        or_(
                            User.email.ilike(search_term),
                            User.first_name.ilike(search_term),
                            User.last_name.ilike(search_term),
                            User.phone.ilike(search_term),
                        )
                    ),
                    Waybill.note.ilike(search_term),
                ),
            )
            .order_by(cls.model.created_at.desc())
        )

        return await paginate(db_session, query)

    @classmethod
    async def commit_waybill(
        cls, db_session: AsyncSession, waybill_id: UUID, user_id: UUID
    ):
        waybill: Waybill = await cls.find_by_id(db_session, waybill_id)

        if not waybill or not waybill.is_pending:
            return waybill  # already committed or not found

        waybill.is_pending = False

        # Получаем все позиции
        offers = waybill.waybill_offers

        for w_offer in offers:
            # Обновляем количество в оффере
            offer: Offer = w_offer.offer
            if waybill.waybill_type in [
                WaybillType.WAYBILL_IN,
                WaybillType.WAYBILL_RETURN,
            ]:
                offer.quantity += w_offer.quantity
            else:
                offer.quantity -= w_offer.quantity

        return waybill
