from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Offer, Product, Waybill, WaybillOffer
from src.schemas.common.enums import WaybillType


class AnalyticalService:
    @staticmethod
    async def get_sold_products(session: AsyncSession):
        """
        SELECT
           p.name,
           p.image_url,
           SUM(waybill_offers.quantity) AS sold,
           SUM(waybill_offers.quantity * waybill_offers.price_rub) AS revenue
        FROM waybills
            JOIN waybill_offers ON waybills.id = waybill_offers.waybill_id
            JOIN offers o ON waybill_offers.offer_id = o.id
            JOIN products p ON o.product_id = p.id
        WHERE waybills.is_pending = false and waybills.waybill_type = 'WAYBILL_OUT'
        GROUP BY p.name
        ORDER BY sold DESC;
        """
        query = (
            select(
                Product.name,
                Product.image_url,
                func.sum(WaybillOffer.quantity).label("sold"),
                func.sum(WaybillOffer.quantity * WaybillOffer.price_rub).label(
                    "revenue"
                ),
            )
            .join(Offer, Offer.id == WaybillOffer.offer_id)
            .join(Product, Product.id == Offer.product_id)
            .join(Waybill, Waybill.id == WaybillOffer.waybill_id)
            .where(~Waybill.is_pending, Waybill.waybill_type == WaybillType.WAYBILL_OUT)
            .group_by(Product.name, Product.image_url)
            .order_by(func.sum(WaybillOffer.quantity).desc())
        )

        result = await session.execute(query)
        rows = result.all()

        return rows
