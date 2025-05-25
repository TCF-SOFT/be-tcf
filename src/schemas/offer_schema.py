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

    price_rub: float = Field(..., examples=[1000])
    super_wholesale_price_rub: float | None = Field(None, examples=[500])
    quantity: int = Field(..., examples=[2])

    image_url: Optional[str] = Field(
        None, examples=["https://storage.yandexcloud.net/tcf-images/default.svg"]
    )
    product_id: UUID = Field(..., examples=["b41f51ed-1969-461e-a966-7dd7d0752c9e"])

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class OfferSchema(_OfferBase):
    id: UUID
    offer_bitrix_id: Optional[str] = Field(None, examples=["278495"])


class OfferPostSchema(_OfferBase):
    pass


class OfferPutSchema(_OfferBase):
    pass
