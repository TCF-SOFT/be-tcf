import uuid

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
)
from pydantic_extra_types.phone_numbers import PhoneNumber

from src.schemas.common.enums import CustomerType, Role, ShippingMethod


class _BaseUser(BaseModel):
    clerk_id: str | None
    email: EmailStr | str
    first_name: str = Field(..., examples=["Vasilii"])
    last_name: str = Field(..., examples=["Pinov"])
    is_active: bool = True
    role: Role = Field("USER", examples=[Role.USER])

    # --------------------------------------------------
    #      Customer Only Fields - Public Metadata
    # --------------------------------------------------
    customer_type: CustomerType = Field(
        default="USER_RETAIL", examples=[CustomerType.USER_RETAIL]
    )
    mailing: bool = False
    phone: PhoneNumber | None = Field(None, examples=["+441234567890"])
    city: str | None = Field(None, examples=["Sevastopol"])
    notes: str | None = None
    shipping_method: ShippingMethod | None = Field(
        None, examples=[ShippingMethod.CARGO]
    )
    shipping_company: str | None = Field(None, examples=["КИТ"])


class UserSchema(_BaseUser):
    id: uuid.UUID
    # addresses: list[AddressSchema] = Field(default_factory=list)


class UserCreate(_BaseUser):
    pass


class UserUpdate(_BaseUser):
    pass
