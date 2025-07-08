from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber

from src.schemas.common.enums import OrderStatus


class _OrderBase(BaseModel):
    user_id: UUID
    address_id: UUID
    status: OrderStatus
    note: str | None = None

    model_config = ConfigDict(from_attributes=True)


class OrderSchema(_OrderBase):
    id: UUID
    user_first_name: str = Field(..., examples=["Vasilii"])
    user_last_name: str = Field(..., examples=["Pinov"])
    user_email: EmailStr
    user_phone: PhoneNumber | None = Field(None, examples=["+441234567890"])

    total_sum: float

    # maybe add address fields or total_sum


class OrderPostSchema(_OrderBase):
    pass


class OrderPatchSchema(BaseModel):
    pass
