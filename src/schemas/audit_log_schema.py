from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, HttpUrl

from schemas.user_schema import UserSchema


class Method(StrEnum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class AuditLogSchema(BaseModel):
    id: UUID
    user_id: UUID
    method: Method | str
    endpoint: HttpUrl | str
    payload: dict | None = None

    user: UserSchema

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
