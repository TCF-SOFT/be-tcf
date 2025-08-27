from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from src.schemas.common.enums import WaybillType
from src.schemas.user_schema import UserSchema
from src.schemas.waybill_offer_schema import WaybillOfferPostSchema


class _WaybillBaseSchema(BaseModel):
    customer_id: UUID | None = None
    order_id: UUID | None = None
    waybill_type: WaybillType = Field(..., examples=[WaybillType.WAYBILL_OUT])
    is_pending: bool = Field(..., examples=[True])
    note: str | None = None

    model_config = ConfigDict(from_attributes=True)


class WaybillSchema(_WaybillBaseSchema):
    id: UUID
    author: UserSchema
    customer: UserSchema

    created_at: datetime
    updated_at: datetime

    # offers: list[OfferSchema]


class WaybillPostSchema(_WaybillBaseSchema):
    author_id: UUID


class WaybillPatchSchema(_WaybillBaseSchema):
    pass


class WaybillWithOffersPostSchema(_WaybillBaseSchema):
    waybill_offers: list[WaybillOfferPostSchema] = Field(
        default_factory=list,
        description="List of offers would be added to Waybill",
    )

class WaybillWithOffersInternalPostSchema(_WaybillBaseSchema):
    author_id: UUID
    waybill_offers: list[WaybillOfferPostSchema] = Field(
        default_factory=list,
        description="List of offers would be added to Waybill",
    )

