from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dao.base import BaseDAO
from src.models.models import Offer, StockMovement, Waybill


class WaybillDAO(BaseDAO):
    model = Waybill

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
            if waybill.type == "in":
                offer.quantity += w_offer.quantity
            else:
                offer.quantity -= w_offer.quantity

            # Создаем движение
            movement = StockMovement(
                offer_id=offer.id,
                waybill_id=waybill.id,
                type=waybill.type,
                quantity=w_offer.quantity,
                user_id=user_id,
                comment=f"Waybill commit: {waybill.id}",
                reverted=False,
            )
            db_session.add(movement)

        await db_session.commit()
        return waybill
