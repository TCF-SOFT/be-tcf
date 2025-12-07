from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
)
from pydantic_extra_types.phone_numbers import PhoneNumber

from src.schemas.common.enums import CustomerType, Role, ShippingMethod


class _BaseUser(BaseModel):
    id: UUID
    clerk_id: str | None
    email: EmailStr | str
    first_name: str = Field(..., examples=["Vasilii"])
    last_name: str = Field(..., examples=["Pinov"])
    is_active: bool = True
    role: Role = Field(Role.USER, examples=[Role.USER])
    balance_rub: int
    balance_usd: int
    balance_eur: int
    balance_try: int

    # --------------------------------------------------
    #      Customer Only Fields - Public Metadata
    # --------------------------------------------------
    customer_type: CustomerType = Field(
        default=CustomerType.USER_RETAIL, examples=[CustomerType.USER_RETAIL]
    )
    mailing: bool = False
    phone: PhoneNumber | None = Field(None, examples=["+441234567890"])
    city: str | None = Field(None, examples=["Sevastopol"])
    note: str | None = None
    shipping_method: ShippingMethod | None = Field(
        None, examples=[ShippingMethod.CARGO]
    )
    shipping_company: str | None = Field(None, examples=["КИТ"])

    model_config = ConfigDict(
        from_attributes=True,
    )


class UserSchema(_BaseUser):
    # addresses: list[AddressSchema] = Field(default_factory=list)
    pass


class UserCreate(_BaseUser):
    pass


class UserUpdate(_BaseUser):
    pass
