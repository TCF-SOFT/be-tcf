from uuid import UUID

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dao.audit_log_dao import AuditLogDAO
from src.schemas.audit_log_schema import AuditLogSchema, Method
from src.utils.logging import logger


async def save_log_entry(
    db_session: AsyncSession,
    user_id: UUID,
    request: Request,
) -> None:
    """
    Save an action audit log to the database.
    """

    if request.method != Method.GET:
        try:
            payload = await request.json()
        except Exception as e:
            logger.warning("Failed to create audit log: %s", e)
            payload = None

        entry_log = AuditLogSchema(
            user_id=user_id,
            method=request.method,
            endpoint=str(request.url),
            payload=payload,
        )

        await AuditLogDAO.add(db_session, **entry_log.model_dump())
