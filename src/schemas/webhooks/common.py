from pydantic import BaseModel, Field, computed_field

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

    # created_at: int
    email_address: str
    id: str
    # linked_to: list[str]
    # matches_sso_connection: bool
    object: str
    # reserved: bool
    # updated_at: int
    # verification: Verification


class PublicMetadata(BaseModel):
    """
    Represents the public metadata structure for Clerk webhook events.
    """

    role: Role = Role.USER


class UserWebhookData(BaseModel):
    """
    Represents the data structure for a user creation event in Clerk webhook events.
    """

    email_addresses: list[EmailAddress]

    first_name: str
    clerk_id: str = Field(..., alias="id")
    # image_url: str | None
    # last_active_at: int
    last_name: str
    phone_numbers: list[dict]
    primary_email_address_id: str
    primary_phone_number_id: str | None

    @computed_field
    @property
    def email(self) -> str:
        """
        Returns the primary email address of the user.
        """
        primary_email = None
        for email in self.email_addresses:
            if email.id == self.primary_email_address_id:
                primary_email = email.email_address
                break

        return primary_email

    @computed_field
    def phone(self) -> str | None:
        """
        Returns the primary phone number of the user.
        """
        if len(self.phone_numbers) > 0 and self.primary_phone_number_id:
            for phone in self.phone_numbers:
                if phone.id == self.primary_phone_number_id:
                    return phone.get("phone_number", None)
        return None
