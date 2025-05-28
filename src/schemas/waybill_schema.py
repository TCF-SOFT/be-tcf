from typing import Literal
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class _WaybillBaseSchema(BaseModel):
    user_id: UUID
    type: Literal["in", "out"]
    is_pending: bool = Field(..., examples=[False])
    counterparty_name: str = Field(
        ..., examples=["ООО Рога и Копыта"]
    )

    model_config = ConfigDict(from_attributes=True)


class WaybillSchema(_WaybillBaseSchema):
    id: UUID


class WaybillPostSchema(_WaybillBaseSchema):
    pass


class WaybillPutSchema(_WaybillBaseSchema):
    pass
