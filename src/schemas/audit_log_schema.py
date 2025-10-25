from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, HttpUrl

from src.schemas.user_schema import UserSchema


class Method(StrEnum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class _AuditLogBaseSchema(BaseModel):
    user_id: UUID
    method: Method | str
    endpoint: HttpUrl | str
    payload: dict | None = None

    model_config = ConfigDict(from_attributes=True)


class AuditLogSchema(_AuditLogBaseSchema):
    id: UUID
    user: UserSchema
    created_at: datetime
    updated_at: datetime


class AuditLogPostSchema(_AuditLogBaseSchema):
    pass
