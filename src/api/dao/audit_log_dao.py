from src.api.dao.base import BaseDAO
from src.models import AuditLog


class AuditLogDAO(BaseDAO):
    model = AuditLog
