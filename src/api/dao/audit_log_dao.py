from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from src.api.dao.base import BaseDAO
from src.models import AuditLog
from src.schemas.audit_log_schema import AuditLogSchema


class AuditLogDAO(BaseDAO):
    model = AuditLog

    @classmethod
    async def find_all_paginate(
        cls, db_session, filter_by: dict
    ) -> Page[AuditLogSchema]:
        query = (
            select(cls.model)
            .filter_by(**filter_by)
            .order_by(cls.model.created_at.desc())
        )
        return await paginate(db_session, query)
