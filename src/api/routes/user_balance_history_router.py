from uuid import UUID

from fastapi import APIRouter, status
from fastapi.params import Depends
from fastapi_pagination import Page

from src.api.auth.clerk import require_role
from src.api.dao.user_balance_history_dao import UserBalanceHistoryDAO
from src.api.di.db_helper import db_helper
from src.schemas.common.enums import Role
from src.schemas.user_balance_history import UserBalanceHistorySchema

router = APIRouter(
    tags=["User Balance History"],
    prefix="/balance",
    dependencies=[Depends(require_role(Role.EMPLOYEE))],
)


@router.get(
    "/{user_id}/history",
    response_model=Page[UserBalanceHistorySchema],
    summary="Return user balance change history",
    status_code=status.HTTP_200_OK,
)
async def get_user_balance_history(
    user_id: UUID, db_session=Depends(db_helper.session_getter)
):
    filters = {"user_id": user_id}
    return await UserBalanceHistoryDAO.find_all_paginate(db_session, filters)
