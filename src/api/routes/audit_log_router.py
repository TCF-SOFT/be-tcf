from fastapi import APIRouter, status
from fastapi.params import Depends

from src.api.auth.clerk import require_role
from src.api.dao.audit_log_dao import AuditLogDAO
from src.api.di.db_helper import db_helper
from src.schemas.audit_log_schema import AuditLogSchema
from src.schemas.common.enums import Role
from src.utils.pagination import Page

router = APIRouter(
    tags=["Audit Log"],
    prefix="/audit-log",
    dependencies=[Depends(require_role(Role.EMPLOYEE))],
)


@router.get(
    "",
    response_model=Page[AuditLogSchema],
    summary="Return all audit logs with pagination",
    status_code=status.HTTP_200_OK,
)
async def get_audit_logs(db_session=Depends(db_helper.session_getter)):
    filters = {}
    return await AuditLogDAO.find_all_paginate(db_session, filters)
