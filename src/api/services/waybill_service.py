from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dao.offer_dao import OfferDAO
from src.api.dao.user_dao import UserDAO
from src.schemas.common.enums import CustomerType
from src.api.dao.waybill_dao import WaybillDAO
from src.api.dao.waybill_offer_dao import WaybillOfferDAO
from src.models import Offer, Waybill, WaybillOffer
from src.schemas.offer_schema import OfferSchema
from src.schemas.waybill_offer_schema import WaybillOfferPostSchema, WaybillOfferSchema
from src.schemas.waybill_schema import WaybillWithOffersPostSchema


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
        """
        <Create from Cart>
        Flow:
        1. Fetch Offer, Waybill, User
        2. Check for customer type
        # TODO: how about IN/RETURN? Цена будет переписана
        3. Assign new price to waybill_offer instance

        """
        offer: Offer = await OfferDAO.find_by_id(db_session, waybill_offer.offer_id)
        waybill: Waybill = await WaybillDAO.find_by_id(db_session, waybill_id)

        customer_type = CustomerType.USER_RETAIL
        if waybill.customer_id:
            customer = await UserDAO.find_by_id(db_session, waybill.customer.id)
            customer_type = customer.customer_type

        match customer_type:
            case CustomerType.USER_SUPER_WHOLESALE:
                price = offer.super_wholesale_price_rub
            case CustomerType.USER_WHOLESALE:
                price = round((offer.price_rub + offer.super_wholesale_price_rub) / 2)
            case _:
                price = offer.price_rub

        return await WaybillOfferDAO.add(
            db_session,
            waybill_id=waybill_id,
            offer_id=waybill_offer.offer_id,
            quantity=waybill_offer.quantity,
            brand=waybill_offer.brand,
            manufacturer_number=waybill_offer.manufacturer_number,
            price_rub=price,
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

    @staticmethod
    async def post_waybill_with_offers(
        db_session: AsyncSession,
        payload: WaybillWithOffersPostSchema,
    ) -> Waybill:
        """
        Create a new waybill with offers.
        """
        async with db_session.begin():
            waybill: Waybill = await WaybillDAO.add(
                db_session, **payload.model_dump(exclude={"waybill_offers"})
            )
            for wo in payload.waybill_offers:
                await WaybillService.add_offer_to_waybill(db_session, waybill.id, wo)

        await db_session.refresh(waybill, ["author", "customer", "waybill_offers"])
        return waybill
