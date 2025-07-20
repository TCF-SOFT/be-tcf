from pydantic import BaseModel

from src.schemas.common.enums import Role


class Verification(BaseModel):
    attempts: int
    expire_at: float
    status: str
    strategy: str


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
    verification: Verification


class PublicMetadata(BaseModel):
    """
    Represents the public metadata structure for Clerk webhook events.
    """

    role: Role


class UserWebhookData(BaseModel):
    """
    Represents the data structure for a user creation event in Clerk webhook events.
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
