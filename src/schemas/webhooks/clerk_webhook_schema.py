from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.webhooks.common import UserWebhookData


class DeleteUserWebhookData(BaseModel):
    """
    Represents the data structure for a user deletion event in Clerk webhook events.
    """

    deleted: bool
    clerk_id: str = Field(..., alias="id")
    object: str


class EventType(StrEnum):
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"


class HttpRequest(BaseModel):
    """
    Represents the HTTP request structure for Clerk webhook events.
    """

    client_ip: str
    user_agent: str


class EventAttributes(BaseModel):
    http_request: HttpRequest


class _WebhookSchema(BaseModel):
    """
    Base schema for Clerk webhook events.
    """

    event_attributes: EventAttributes
    # instance_id: str
    object: str
    timestamp: float
    type: EventType

    model_config = ConfigDict(validate_by_name=True)


class UserWebhookSchema(_WebhookSchema):
    """
    Schema for the user.created event in Clerk webhooks.
    Schema for the user.updated event in Clerk webhooks.
    Schema for the user.deleted event in Clerk webhooks.
    """

    data: UserWebhookData | DeleteUserWebhookData
