from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, HttpUrl


class Method(StrEnum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class AuditLogSchema(BaseModel):
    user_id: UUID
    method: Method | str
    endpoint: HttpUrl | str
    payload: dict | None = None

    model_config = ConfigDict(from_attributes=True)
