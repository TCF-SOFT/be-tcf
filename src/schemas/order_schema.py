from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.schemas.common.enums import OrderStatus


class _OrderBase(BaseModel):
    id: UUID
    user_id: UUID
    address_id: UUID
    status: OrderStatus
    note: str | None = None

    model_config = ConfigDict(from_attributes=True)


class OrderSchema(_OrderBase):
    pass
