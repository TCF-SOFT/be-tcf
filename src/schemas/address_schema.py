from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from pydantic_extra_types.phone_numbers import PhoneNumber

from src.schemas.common.enums import ShippingMethod


class _AddressBase(BaseModel):
    user_id: UUID
    first_name: str
    last_name: str
    phone: PhoneNumber | None = Field(None, examples=["+441234567890"])

    city: str | None = Field(None, examples=["Sevastopol"])
    street: str = Field(..., examples=["Мясницкая 20"])
    postal_code: str = Field(..., examples=["101000"])

    shipping_method: ShippingMethod | None = Field(
        None, examples=[ShippingMethod.CARGO]
    )
    shipping_company: str | None = Field(None, examples=["КИТ"])
    is_default: bool = True

    model_config = ConfigDict(from_attributes=True)


class AddressSchema(_AddressBase):
    id: UUID


class AddressPostSchema(_AddressBase):
    pass

class AddressPatchSchema(_AddressBase):
    pass

