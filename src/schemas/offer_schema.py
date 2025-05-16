from typing import Optional
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class _OfferBase(BaseModel):
    brand: str = Field(..., examples=["MARKON"])
    manufacturer_number: Optional[str] = Field(None, examples=["6000180"])

    internal_description: Optional[str] = Field(
        None, examples=["Колодки тормозные передние"]
    )

    price_rub: float = Field(..., examples=[578.8])
    super_wholesale_price_rub: float | None = Field(None, examples=[579.00])
    quantity: int = Field(..., examples=[2])

    model_config = ConfigDict(from_attributes=True)


class OfferSchema(_OfferBase):
    id: UUID
    product_id: UUID
    offer_bitrix_id: Optional[str] = Field(None, examples=["278495"])

    product_id: UUID = Field(..., examples=["b41f51ed-1969-461e-a966-7dd7d0752c9e"])


class OfferPostSchema(_OfferBase):
    product_id: UUID = Field(..., examples=["b41f51ed-1969-461e-a966-7dd7d0752c9e"])


class OfferPutSchema(_OfferBase):
    pass
