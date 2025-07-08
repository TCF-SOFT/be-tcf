from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.schemas.common.enums import OrderStatus


class _OrderBase(BaseModel):
    user_id: UUID
    address_id: UUID
    status: OrderStatus
    note: str | None = None

    model_config = ConfigDict(from_attributes=True)


class OrderSchema(_OrderBase):
    id: UUID


class OrderPostSchema(_OrderBase):
    pass


class OrderPatchSchema(BaseModel):
    pass
