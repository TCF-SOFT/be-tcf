from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import or_, select

from src.api.dao.base import BaseDAO
from src.models import Order, User
from src.schemas.order_schema import OrderSchema


class OrderDAO(BaseDAO):
    model = Order

    @classmethod
    async def find_all_paginate(
        cls,
        db_session,
        search_term: str,
        filter_by: dict | None = None,
        order_by: str = None,
    ) -> Page[OrderSchema]:
        search_term = f"%{search_term}%"
        query = (
            select(cls.model)
            .filter_by(**filter_by)
            .where(
                or_(
                    Order.user.has(
                        or_(
                            User.email.ilike(search_term),
                            User.first_name.ilike(search_term),
                            User.last_name.ilike(search_term),
                            User.phone.ilike(search_term),
                        )
                    ),
                    Order.note.ilike(search_term),
                ),
            )
            .order_by(cls.model.created_at.desc())
        )

        return await paginate(db_session, query)
