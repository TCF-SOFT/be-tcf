from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class _WaybillBaseSchema(BaseModel):
    user_id: UUID
    waybill_type: Literal["WAYBILL_IN", "WAYBILL_OUT"]
    is_pending: bool = Field(..., examples=[True])
    counterparty_name: str = Field(..., examples=["ООО Рога и Копыта"])

    model_config = ConfigDict(from_attributes=True)


class WaybillSchema(_WaybillBaseSchema):
    id: UUID
    author: str = Field(..., examples=["Vasiliy Pinov"])
    created_at: datetime
    updated_at: datetime


class WaybillPostSchema(_WaybillBaseSchema):
    pass


class WaybillPutSchema(_WaybillBaseSchema):
    pass
