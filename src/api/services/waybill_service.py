from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from schemas.offer_schema import OfferSchema
from src.api.dao.waybill_dao import WaybillDAO
from src.api.dao.waybill_offer_dao import WaybillOfferDAO
from src.models import Offer, Waybill, WaybillOffer
from src.schemas.waybill_offer_schema import WaybillOfferPostSchema, WaybillOfferSchema


class WaybillService:
    """
    Business logic:
    1. Waybill with base info is created
    2. Then User click on edit and start adding fields
    3. Each field is WaybillOffer row. POST /waybill/{id}/offers
    4. Commit waybill. POST /waybill/{id}/commit
    5. Waybill.is_pending → False
    6. Refresh Offer.quantity
    7. Create StockMovement for each WaybillOffer
    """

    @staticmethod
    async def commit(db: AsyncSession, waybill_id: UUID, user_id: UUID) -> Waybill:
        return await WaybillDAO.commit_waybill(db, waybill_id, user_id)

    @staticmethod
    async def add_offer_to_waybill(
        db_session: AsyncSession,
        waybill_id: UUID,
        waybill_offer: WaybillOfferPostSchema,
    ) -> WaybillOffer:
        return await WaybillOfferDAO.add(
            db_session,
            waybill_id=waybill_id,
            offer_id=waybill_offer.offer_id,
            quantity=waybill_offer.quantity,
            brand=waybill_offer.brand,
            manufacturer_number=waybill_offer.manufacturer_number,
            price_rub=waybill_offer.price_rub,
        )

    @staticmethod
    async def fetch_waybill_offers(waybill) -> list[WaybillOfferSchema]:
        result: list[WaybillOfferSchema] = []
        for item in waybill.waybill_offers:
            offer: Offer = item.offer
            result.append(
                WaybillOfferSchema.model_validate(
                    {
                        "id": item.id,
                        "waybill_id": waybill.id,
                        "offer_id": offer.id,
                        "quantity": item.quantity,
                        "brand": item.brand,
                        "manufacturer_number": item.manufacturer_number,
                        "price_rub": item.price_rub,
                        "offer": OfferSchema.model_validate(offer),
                    }
                )
            )
        return result
