from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.controllers.create_entity_controller import create_entity
from api.controllers.update_entity_controller import update_entity
from src.api.dao.order_dao import OrderDAO
from src.api.di.db_helper import db_helper
from src.schemas.common.enums import OrderStatus
from src.schemas.order_schema import OrderPatchSchema, OrderPostSchema, OrderSchema

# Flow:
# 1. Create a cart
# 2. Add offers to the cart
# 3. Create an order from the cart with order_offers for cart_offers
# 4. Flush the cart and cart items
router = APIRouter(tags=["Orders"], prefix="/orders")


@router.get(
    "",
    response_model=list[OrderSchema],
    summary="Return all orders",
    status_code=status.HTTP_200_OK,
)
async def get_orders(
    user_id: UUID | None = None,
    order_status: OrderStatus | None = None,
    db_session: AsyncSession = Depends(db_helper.session_getter),
):
    """
    Get all orders.
    """
    filters = {}
    if user_id:
        filters["user_id"] = user_id
    if order_status:
        filters["status"] = order_status
    return await OrderDAO.find_all(db_session, filter_by=filters)


@router.get(
    "/{order_id}",
    response_model=OrderSchema,
    summary="Return offer by id",
    status_code=status.HTTP_200_OK,
)
async def get_order(
    offer_id: UUID, db_session: AsyncSession = Depends(db_helper.session_getter)
):
    res = await OrderDAO.find_by_id(db_session, offer_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {offer_id} not found.",
        )
    return res


@router.post(
    "",
    response_model=OrderSchema,
    summary="Create a new order",
    status_code=status.HTTP_201_CREATED,
)
async def post_order(
    payload: OrderPostSchema,
    db_session: AsyncSession = Depends(db_helper.session_getter),
):
    return await create_entity(payload=payload, db_session=db_session, dao=OrderDAO)


@router.patch(
    "/{order_id}",
    response_model=OrderSchema,
    summary="Update order by id",
    status_code=status.HTTP_200_OK,
    # dependencies=[Depends(require_employee)],
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
    # dependencies=[Depends(require_employee)],
)
async def delete_order(
    order_id: UUID,
    db_session: AsyncSession = Depends(db_helper.session_getter),
):
    success = await OrderDAO.delete_by_id(db_session, order_id)
    if not success:
        raise HTTPException(status_code=404, detail="Order not found")
