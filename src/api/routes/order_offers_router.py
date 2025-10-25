from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth.clerk import require_role
from src.schemas.common.enums import Role
from src.api.core.update_entity import update_entity
from src.api.dao.order_offer_dao import OrderOfferDAO
from src.api.di.db_helper import db_helper
from src.schemas.order_offer_schema import OrderOfferPatchSchema, OrderOfferSchema

router = APIRouter(
    tags=["Order-Offers"],
    prefix="/order-offers",
    dependencies=[Depends(require_role(Role.EMPLOYEE))],
)


@router.patch(
    "/{order_offer_id}",
    status_code=status.HTTP_200_OK,
    response_model=OrderOfferSchema,
)
async def update_offer_in_order(
    order_offer_id: UUID,
    payload: OrderOfferPatchSchema,
    db_session: AsyncSession = Depends(db_helper.session_getter),
):
    return await update_entity(
        entity_id=order_offer_id,
        payload=payload,
        dao=OrderOfferDAO,
        db_session=db_session,
    )


@router.delete("/{order_offer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_offer_from_order(
    order_offer_id: UUID,
    db_session: AsyncSession = Depends(db_helper.session_getter),
):
    deleted = await OrderOfferDAO.delete_by_id(db_session, order_offer_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Offer not found in order"
        )
    return
