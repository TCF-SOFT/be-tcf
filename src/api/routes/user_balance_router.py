from uuid import UUID

from fastapi import APIRouter, status, HTTPException
from fastapi.params import Depends
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.services.user_balance_service import UserBalanceService
from src.api.auth.clerk import require_role
from src.api.dao.user_balance_history_dao import UserBalanceHistoryDAO
from src.api.di.db_helper import db_helper
from src.schemas.common.enums import Role, UserBalanceChangeReason
from src.schemas.user_balance_history import UserBalanceHistorySchema

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
    try:
        return await UserBalanceHistoryDAO.find_all_paginate(db_session, filters)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post(
    "/adjust/{user_id}",
    response_model=UserBalanceHistorySchema,
    summary="Adjust user balance (Admin only)",
    status_code=status.HTTP_201_CREATED,
    # dependencies=[Depends(require_role(Role.ADMIN))],
)
async def adjust_user_balance(
    user_id: UUID,
    delta: float,
    reason: UserBalanceChangeReason,
    db_session: AsyncSession = Depends(db_helper.session_getter),
):
    try:
        return await UserBalanceService.change_balance(db_session, user_id, delta, reason)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
