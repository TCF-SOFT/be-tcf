from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import delete as sa_delete
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dao.base import BaseDAO
from src.models.user import User
from src.schemas.user_schema import UserSchema
from src.utils.pagination import Page


class UserDAO(BaseDAO):
    model = User

    @classmethod
    async def find_all_paginate(
        cls,
        db_session,
        filter_by: dict,
        search_term: str,
    ) -> Page[UserSchema]:
        search_term = f"%{search_term}%"
        query = (
            select(cls.model)
            .filter_by(**filter_by)
            .where(
                or_(
                    cls.model.first_name.ilike(search_term),
                    cls.model.last_name.ilike(search_term),
                    cls.model.phone.ilike(search_term),
                    cls.model.email.ilike(search_term),
                )
            )
            .order_by(cls.model.created_at.desc())
        )

        return await paginate(db_session, query)
