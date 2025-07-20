from enum import Enum

from pydantic import BaseModel, ConfigDict

from schemas.common.enums import Role


class EventType(str, Enum):
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"


class EmailAddress(BaseModel):
    """
    Represents the structure of an email address in Clerk webhook events.
    """

    created_at: int
    email_address: str
    id: str
    linked_to: list[str]
    matches_sso_connection: bool
    object: str
    reserved: bool
    updated_at: int
    verification: dict


class PublicMetadata(BaseModel):
    """
    Represents the public metadata structure for Clerk webhook events.
    """

    role: Role


class HttpRequest(BaseModel):
    """
    Represents the HTTP request structure for Clerk webhook events.
    """

    client_ip: str
    user_agent: str


class EventAttributes(BaseModel):
    http_request: HttpRequest


class WebhookData(BaseModel):
    """
    Represents the data structure for Clerk webhook events.
    """

    backup_code_enabled: bool
    banned: bool
    create_organization_enabled: bool
    created_at: int
    delete_self_enabled: bool
    email_addresses: list[EmailAddress]
    enterprise_accounts: list[dict]
    external_accounts: list[dict]
    external_id: str | None
    first_name: str
    has_image: bool
    id: str
    image_url: str
    last_active_at: int
    last_name: str
    last_sign_in_at: int | None
    legal_accepted_at: int | None
    locked: bool
    lockout_expires_in_seconds: int | None
    mfa_disabled_at: int | None
    mfa_enabled_at: int | None
    object: str
    passkeys: list[dict]
    password_enabled: bool
    phone_numbers: list[dict]
    primary_email_address_id: str
    primary_phone_number_id: str | None
    primary_web3_wallet_id: str | None
    private_metadata: dict
    profile_image_url: str
    public_metadata: PublicMetadata
    saml_accounts: list[dict]
    totp_enabled: bool
    two_factor_enabled: bool
    unsafe_metadata: dict
    updated_at: int
    username: str | None
    verification_attempts_remaining: int
    web3_wallets: list[dict]


class ClerkWebhookSchema(BaseModel):
    """
    Represents the schema for Clerk webhook events.
    """

    data: WebhookData
    event_attributes: EventAttributes
    instance_id: str
    object: str
    timestamp: float
    type: EventType

    model_config = ConfigDict(validate_by_name=True)
