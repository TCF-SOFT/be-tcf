from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth.better_auth import require_role
from src.api.dao.helper import OrderByOption
from src.api.dao.user_balance_history_dao import UserBalanceHistoryDAO
from src.api.di.db_helper import db_helper
from src.api.services.user_balance_service import UserBalanceService
from src.schemas.common.enums import Currency, Role, UserBalanceChangeReason
from src.schemas.user_balance_history import UserBalanceHistorySchema
from src.utils.pagination import Page

router = APIRouter(
    tags=["User Balance"],
    prefix="/balance",
    # dependencies=[Depends(require_role(Role.USER))],
)


@router.get(
    "/history/{user_id}",
    response_model=Page[UserBalanceHistorySchema],
    summary="Return user balance change history",
    status_code=status.HTTP_200_OK,
)
async def get_user_balance_history(
    user_id: UUID, db_session=Depends(db_helper.session_getter)
):
    filters = {"user_id": user_id}
    order_by: OrderByOption = {"field": "created_at", "direction": "desc"}
    try:
        return await UserBalanceHistoryDAO.find_all_paginate(
            db_session, filters, order_by
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post(
    "/adjust/{user_id}",
    response_model=UserBalanceHistorySchema,
    summary="Adjust user balance (Admin only)",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
async def adjust_user_balance(
    user_id: UUID,
    delta: int,
    reason: UserBalanceChangeReason,
    currency: Currency = Currency.RUB,
    db_session: AsyncSession = Depends(db_helper.session_getter),
):
    try:
        return await UserBalanceService.change_balance(
            db_session, user_id, delta, reason, currency
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
