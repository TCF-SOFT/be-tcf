import uuid

from fastapi_users import schemas
from pydantic import BaseModel, Field, HttpUrl, field_serializer
from pydantic_extra_types.phone_numbers import PhoneNumber

from src.schemas.common.enums import CustomerType, Role, ShippingMethod


class _BaseUser(BaseModel):
    clerk_id: str | None
    first_name: str = Field(..., examples=["Vasilii"])
    last_name: str = Field(..., examples=["Pinov"])
    role: Role = Field("USER", examples=[Role.EMPLOYEE])
    avatar_url: HttpUrl | None = Field(
        None, examples=["https://storage.yandexcloud.net/tcf-images/default.svg"]
    )

    # Customer only fields:
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

    @field_serializer("avatar_url")
    def serialize_avatar_url(self, v):
        return str(v) if v else None


class UserRead(schemas.BaseUser[uuid.UUID], _BaseUser):
    pass


class UserCreate(schemas.BaseUserCreate, _BaseUser):
    pass


class UserUpdate(schemas.BaseUserUpdate, _BaseUser):
    pass
