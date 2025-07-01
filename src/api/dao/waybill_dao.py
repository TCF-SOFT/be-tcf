from uuid import UUID

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.waybill_schema import WaybillSchema
from src.api.dao.base import BaseDAO
from src.models import Offer, StockMovement, Waybill


class WaybillDAO(BaseDAO):
    model = Waybill

    @classmethod
    async def find_all(cls, db_session, filter_by: dict, order_by: str = None) -> list:
        query = select(cls.model).filter_by(**filter_by).order_by(order_by)
        result = await db_session.execute(query)
        res = result.unique().scalars().all()
        return res

    @classmethod
    async def find_all_paginate(
        cls, db_session, filter_by: dict, search_term: str
    ) -> Page[WaybillSchema]:
        query = (
            select(cls.model)
            .filter_by(**filter_by)
            .order_by(cls.model.created_at.desc())
            .where(cls.model.counterparty_name.ilike(f"%{search_term}%"))
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
            if waybill.waybill_type in ["WAYBILL_IN", "WAYBILL_RETURN"]:
                offer.quantity += w_offer.quantity
            else:
                offer.quantity -= w_offer.quantity

            # Создаем движение
            movement = StockMovement(
                offer_id=offer.id,
                waybill_id=waybill.id,
                waybill_type=waybill.waybill_type,
                quantity=w_offer.quantity,
                user_id=user_id,
                comment=f"Waybill commit: {waybill.id}",
                reverted=False,
            )
            db_session.add(movement)

        return waybill
