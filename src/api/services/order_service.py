from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dao.offer_dao import OfferDAO
from src.api.dao.order_dao import OrderDAO
from src.api.dao.order_offer_dao import OrderOfferDAO
from src.api.dao.user_dao import UserDAO
from src.models import Offer, Order, OrderOffer
from src.schemas.common.enums import CustomerType
from src.schemas.offer_schema import OfferSchema
from src.schemas.order_offer_schema import OrderOfferPostSchema, OrderOfferSchema
from src.schemas.order_schema import OrderWithOffersPostSchema


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
        offer: Offer = await OfferDAO.find_by_id(db_session, order_offer.offer_id)
        order: Order = await OrderDAO.find_by_id(db_session, order_id)

        customer_type = CustomerType.USER_RETAIL
        if order.user.customer_type:
            customer = await UserDAO.find_by_id(db_session, order.user.id)
            customer_type = customer.customer_type

        match customer_type:
            case CustomerType.USER_SUPER_WHOLESALE:
                price = offer.super_wholesale_price_rub
            case CustomerType.USER_WHOLESALE:
                price = round((offer.price_rub + offer.super_wholesale_price_rub) / 2)
            case _:
                price = offer.price_rub

        return await OrderOfferDAO.add(
            db_session,
            order_id=order_id,
            offer_id=order_offer.offer_id,
            quantity=order_offer.quantity,
            brand=order_offer.brand,
            manufacturer_number=order_offer.manufacturer_number,
            price_rub=price,
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

    @staticmethod
    async def post_order_with_offers(
        db_session: AsyncSession,
        payload: OrderWithOffersPostSchema,
    ) -> Order:
        """
        Add an offer to an order and return the created OrderOffer schema.
        """
        order: Order = await OrderDAO.add(
            db_session, **payload.model_dump(exclude={"order_offers"})
        )
        for order_offer in payload.order_offers:
            await OrderService.add_offer_to_order(db_session, order.id, order_offer)
        await db_session.commit()
        await db_session.refresh(order, ["user", "order_offers"])
        return order
