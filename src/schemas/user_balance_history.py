from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from schemas.common.enums import Currency, UserBalanceReason
from schemas.user_schema import UserSchema
from schemas.waybill_schema import WaybillSchema


class _UserBalanceHistoryBaseSchema(BaseModel):
    user_id: UUID
    waybill_id: UUID | None
    delta: float
    currency: Currency = Currency.RUB
    balance_before: float
    balance_after: float
    reason: UserBalanceReason

    model_config = ConfigDict(from_attributes=True)


class UserBalanceHistorySchema(_UserBalanceHistoryBaseSchema):
    id: UUID
    user: UserSchema
    waybill: WaybillSchema | None
    created_at: datetime
    updated_at: datetime


class UserBalanceHistoryPostSchema(_UserBalanceHistoryBaseSchema):
    pass
