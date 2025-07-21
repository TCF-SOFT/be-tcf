from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from schemas.common.enums import WaybillType
from schemas.user_schema import UserSchema


class _WaybillBaseSchema(BaseModel):
    user_id: UUID
    waybill_type: WaybillType = Field(..., examples=[WaybillType.WAYBILL_OUT])
    is_pending: bool = Field(..., examples=[True])
    counterparty_name: str = Field(..., examples=["ООО Рога и Копыта"])
    note: str | None = None

    model_config = ConfigDict(from_attributes=True)


class WaybillSchema(_WaybillBaseSchema):
    id: UUID
    user: UserSchema

    created_at: datetime
    updated_at: datetime

    # offers: list[OfferSchema]


class WaybillPostSchema(_WaybillBaseSchema):
    pass


class WaybillPutSchema(_WaybillBaseSchema):
    pass
