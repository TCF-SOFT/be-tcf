from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.address_schema import AddressSchema
from src.schemas.common.enums import OrderStatus
from src.schemas.order_offer_schema import OrderOfferPostSchema, OrderOfferSchema
from src.schemas.user_schema import UserSchema
from src.schemas.waybill_schema import WaybillSchema


class _OrderBaseSchema(BaseModel):
    address_id: UUID = Field(..., examples=["356f1d6f-0514-4e40-aad5-d59b91674320"])
    status: OrderStatus
    note: str | None = None

    model_config = ConfigDict(from_attributes=True)


class OrderSchema(_OrderBaseSchema):
    id: UUID
    user: UserSchema
    address: AddressSchema
    waybill: WaybillSchema | None = None
    order_offers: list[OrderOfferSchema]
    total_sum: float

    created_at: datetime
    updated_at: datetime


class OrderPostSchema(_OrderBaseSchema):
    pass


class OrderPatchSchema(_OrderBaseSchema):
    pass


class OrderWithOffersPostSchema(_OrderBaseSchema):
    order_offers: list[OrderOfferPostSchema] = Field(
        default_factory=list,
        description="List of offers to be added to the Order",
    )


class OrderWithOffersInternalPostSchema(_OrderBaseSchema):
    """
    Internal schema with injected user_id
    Injection happens in the route layer from JWT
    Used to remove user_id from the public schema on Frontend
    """

    user_id: UUID = Field(..., examples=["13a6f665-da25-4868-92c3-4e6a39dd3c6f"])
    order_offers: list[OrderOfferPostSchema] = Field(
        default_factory=list,
        description="List of offers to be added to the Order",
    )
