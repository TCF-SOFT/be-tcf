from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.schemas.common.enums import Currency, UserBalanceChangeReason
from src.schemas.waybill_schema import WaybillSchema


class _UserBalanceHistoryBaseSchema(BaseModel):
    user_id: UUID
    waybill_id: UUID | None
    delta: float
    currency: Currency = Currency.RUB
    balance_before: float
    balance_after: float
    reason: UserBalanceChangeReason

    model_config = ConfigDict(from_attributes=True)


class UserBalanceHistorySchema(_UserBalanceHistoryBaseSchema):
    id: UUID
    waybill: WaybillSchema | None
    created_at: datetime
    updated_at: datetime


class UserBalanceHistoryPostSchema(_UserBalanceHistoryBaseSchema):
    pass
