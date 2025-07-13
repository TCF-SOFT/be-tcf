from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dao.order_offer_dao import OrderOfferDAO
from src.models import Offer, OrderOffer
from src.schemas.offer_schema import OfferSchema
from src.schemas.order_offer_schema import OrderOfferPostSchema, OrderOfferSchema


class OrderService:
    """
    Business logic:
    1. Order with base info is created
    2. Then Admin could add offers to the order
    3. Each field is OrderOffer row. POST /order/{id}/offers
    4. Commit order. POST /order/{id}/commit
    5. Order.is_pending → False ??
    6. Refresh Offer.quantity
    7. Create StockMovement for each OrderOffer
    """

    # @staticmethod
    # async def commit(db: AsyncSession, order_id: UUID, user_id: UUID) -> Order:
    #     return await OrderDAO.commit_order(db, order_id, user_id)

    @staticmethod
    async def add_offer_to_order(
        db_session: AsyncSession,
        order_id: UUID,
        order_offer: OrderOfferPostSchema,
    ) -> OrderOffer:
        return await OrderOfferDAO.add(
            db_session,
            order_id=order_id,
            offer_id=order_offer.offer_id,
            quantity=order_offer.quantity,
            brand=order_offer.brand,
            manufacturer_number=order_offer.manufacturer_number,
            price_rub=order_offer.price_rub,
        )

    @staticmethod
    async def fetch_order_offers(order) -> list[OrderOfferSchema]:
        result: list[OrderOfferSchema] = []
        for item in order.order_offers:
            offer: Offer = item.offer
            result.append(
                OrderOfferSchema.model_validate(
                    {
                        "id": item.id,
                        "order_id": order.id,
                        "offer_id": offer.id,
                        "quantity": item.quantity,
                        "brand": offer.brand,
                        "manufacturer_number": offer.manufacturer_number,
                        "price_rub": item.price_rub,
                        "offer": OfferSchema.model_validate(offer),
                    }
                )
            )
        return result
