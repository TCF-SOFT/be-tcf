from typing import Optional
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
)


class _OfferBase(BaseModel):
    brand: str = Field(..., examples=["MARKON"])
    manufacturer_number: Optional[str] = Field(None, examples=["6000180"])

    internal_description: Optional[str] = Field(
        None, examples=["Колодки тормозные передние"]
    )

    price_rub: float = Field(..., examples=[1000])
    super_wholesale_price_rub: float = Field(None, examples=[500])

    quantity: int = Field(..., examples=[2])
    product_id: UUID = Field(..., examples=["b41f51ed-1969-461e-a966-7dd7d0752c9e"])

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class OfferSchema(_OfferBase):
    id: UUID
    offer_bitrix_id: Optional[str] = Field(None, examples=["278495"])
    category_slug: str = Field(..., examples=["svechi-ford"])
    sub_category_slug: str = Field(..., examples=["svechi-zazhiganiia"])

    image_url: Optional[str] = Field(
        None, examples=["https://storage.yandexcloud.net/tcf-images/default.svg"]
    )

    @computed_field
    @property
    def wholesale_price_rub(self) -> int:
        return int((self.price_rub + self.super_wholesale_price_rub) / 2)


class OfferPostSchema(_OfferBase):
    pass


class OfferPutSchema(_OfferBase):
    pass
