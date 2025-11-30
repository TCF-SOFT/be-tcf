from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth.clerk import require_role
from src.api.core.update_entity import update_entity
from src.api.dao.offer_dao import OfferDAO
from src.api.dao.order_dao import OrderDAO
from src.api.di.db_helper import db_helper
from src.api.services.order_service import OrderService
from src.models import Order, Product
from src.schemas.common.enums import OrderStatus, Role
from src.schemas.offer_schema import OfferSchema
from src.schemas.order_offer_schema import (
    OrderOfferPostSchema,
    OrderOfferSchema,
)
from src.schemas.order_schema import (
    OrderPatchSchema,
    OrderSchema,
    OrderWithOffersInternalPostSchema,
    OrderWithOffersPostSchema,
)
from src.schemas.waybill_schema import WaybillSchema
from src.utils.pagination import Page

# Flow:
# 1. Create a cart
# 2. Add offers to the cart
# 3. Create an order from the cart with order_offers for cart_offers
# 4. Flush the cart and cart items
# 5. Convert order to waybill
router = APIRouter(
    tags=["Orders"],
    prefix="/orders",
)


@router.get(
    "",
    response_model=Page[OrderSchema],
    summary="Return all orders",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_role(Role.USER))],
)
async def get_orders(
    db_session: AsyncSession = Depends(db_helper.session_getter),
    user_id: UUID | None = None,
    order_status: OrderStatus | None = None,
    search_term: str = "",
):
    filters = {}
    if user_id:
        filters["user_id"] = user_id
    if order_status:
        filters["status"] = order_status
    return await OrderDAO.find_all_paginate(
        db_session, filter_by=filters, search_term=search_term
    )


@router.get(
    "/{order_id}",
    response_model=OrderSchema,
    summary="Return offer by id",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_role(Role.USER))],
)
async def get_order(
    order_id: UUID, db_session: AsyncSession = Depends(db_helper.session_getter)
):
    res = await OrderDAO.find_by_id(db_session, order_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {order_id} not found.",
        )
    return res


@router.get(
    "/{order}/offers",
    status_code=status.HTTP_200_OK,
    response_model=list[OrderOfferSchema],
    dependencies=[Depends(require_role(Role.USER))],
)
async def get_order_offers(
    order: UUID, db_session: AsyncSession = Depends(db_helper.session_getter)
):
    """
    Get all offers in order
    """
    order: Order = await OrderDAO.find_by_id(db_session, order)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )

    return await OrderService.fetch_order_offers(order)


@router.get(
    "/meta/count",
    response_model=dict[str, int],
    summary="Return count of orders",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_role(Role.EMPLOYEE))],
)
async def count_orders(
    order_status: OrderStatus | None = None,
    user_id: UUID | None = None,
    db_session: AsyncSession = Depends(db_helper.session_getter),
):
    filters = {}

    if order_status:
        filters["status"] = order_status

    if user_id:
        filters["user_id"] = user_id

    return await OrderDAO.count_all(db_session, filter_by=filters)


@router.post(
    "",
    response_model=OrderSchema,
    summary="Create a new order",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(Role.USER))],
)
async def post_order(
    payload: OrderWithOffersPostSchema,
    user_id: UUID = Depends(require_role(Role.USER)),
    db_session: AsyncSession = Depends(db_helper.session_getter_manual),
):
    internal = OrderWithOffersInternalPostSchema(
        user_id=user_id,
        **payload.model_dump(),
    )
    return await OrderService.post_order_with_offers(db_session, internal)


@router.post(
    "/{order_id}/offers",
    status_code=status.HTTP_201_CREATED,
    response_model=OrderOfferSchema,
    dependencies=[Depends(require_role(Role.EMPLOYEE))],
)
async def add_offer_to_order(
    order_id: UUID,
    order_offer: OrderOfferPostSchema,
    db_session: AsyncSession = Depends(db_helper.session_getter),
):
    # получаем текущие данные из offers — для валидации
    offer = await OfferDAO.find_by_id(db_session, order_offer.offer_id)
    if not offer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Offer not found"
        )

    product: Product = offer.product
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    order_offer_obj = await OrderService.add_offer_to_order(
        db_session, order_id, order_offer
    )

    return OrderOfferSchema(
        id=order_offer_obj.id,
        order_id=order_id,
        offer_id=offer.id,
        offer=OfferSchema.model_validate(offer),
        quantity=order_offer_obj.quantity,
        brand=order_offer_obj.brand,
        manufacturer_number=order_offer_obj.manufacturer_number,
        price_rub=order_offer_obj.price_rub,
    )


@router.post(
    "/{order_id}/convert",
    response_model=WaybillSchema,
    summary="Convert order to waybill",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(Role.EMPLOYEE))],
)
async def convert_order_to_waybill(
    order_id: UUID,
    author_id: UUID = Depends(require_role(Role.EMPLOYEE)),
    db_session: AsyncSession = Depends(db_helper.session_getter_manual),
):
    """
    Convert an order to a waybill.
    This will create a waybill from the order and flush the order.
    """
    order = await OrderDAO.find_by_id(db_session, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )
    if order.waybill:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order is already converted to a waybill",
        )

    return await OrderService.convert_order_to_waybill(db_session, order, author_id)


@router.patch(
    "/{order_id}",
    response_model=OrderSchema,
    summary="Update order by id",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_role(Role.EMPLOYEE))],
)
async def patch_order(
    order_id: UUID,
    payload: OrderPatchSchema,
    db_session: AsyncSession = Depends(db_helper.session_getter),
):
    return await update_entity(
        entity_id=order_id, payload=payload, dao=OrderDAO, db_session=db_session
    )


@router.delete(
    "/{order_id}",
    summary="Delete order by id",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
async def delete_order(
    order_id: UUID,
    db_session: AsyncSession = Depends(db_helper.session_getter),
):
    success = await OrderDAO.delete_by_id(db_session, order_id)
    if not success:
        raise HTTPException(status_code=404, detail="Order not found")
