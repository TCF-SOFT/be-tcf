from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dao.order_dao import OrderDAO
from src.api.di.db_helper import db_helper
from src.schemas.order_schema import OrderSchema

router = APIRouter(tags=["Orders"], prefix="/orders")


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
