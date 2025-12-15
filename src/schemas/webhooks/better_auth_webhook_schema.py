from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel


class EventType(StrEnum):
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"


class BetterAuthUserData(BaseModel):
    id: UUID
    email: str
    first_name: str
    last_name: str
    image: str | None = None
    createdAt: str | None = None
    updatedAt: str | None = None


class BetterAuthWebhookSchema(BaseModel):
    type: EventType
    data: BetterAuthUserData  # only user.created and user.updated events
