from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.address_schema import AddressSchema
from src.schemas.common.enums import OrderStatus
from src.schemas.order_offer_schema import OrderOfferSchema
from src.schemas.user_schema import UserSchema


class _OrderBase(BaseModel):
    user_id: UUID = Field(..., examples=["13a6f665-da25-4868-92c3-4e6a39dd3c6f"])
    address_id: UUID = Field(..., examples=["356f1d6f-0514-4e40-aad5-d59b91674320"])
    status: OrderStatus
    note: str | None = None

    model_config = ConfigDict(from_attributes=True)


class OrderSchema(_OrderBase):
    id: UUID
    user: UserSchema
    address: AddressSchema
    order_offers: list[OrderOfferSchema]
    total_sum: float

    created_at: datetime
    updated_at: datetime


class OrderPostSchema(_OrderBase):
    pass


class OrderPatchSchema(BaseModel):
    pass
