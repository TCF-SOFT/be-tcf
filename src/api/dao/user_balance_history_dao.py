from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from src.api.dao.base import BaseDAO
from src.models import UserBalanceHistory
from src.schemas.user_balance_history import UserBalanceHistorySchema


class UserBalanceHistoryDAO(BaseDAO):
    model = UserBalanceHistory

    @classmethod
    async def find_all_paginate(
        cls, db_session, filter_by: dict
    ) -> Page[UserBalanceHistorySchema]:
        query = (
            select(cls.model)
            .filter_by(**filter_by)
            .order_by(cls.model.created_at.desc())
        )
        return await paginate(db_session, query)
