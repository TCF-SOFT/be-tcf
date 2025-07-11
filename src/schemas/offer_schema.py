from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
)

from src.schemas.product_schema import ProductSchema


class _OfferBase(BaseModel):
    address_id: str | None = Field(None, examples=["AA-TEST"])
    brand: str = Field(..., examples=["MARKON"])
    manufacturer_number: str = Field(..., examples=["6000180"])

    internal_description: str | None = Field(
        None, examples=["Колодки тормозные передние"]
    )

    price_rub: float = Field(..., examples=[1000])
    super_wholesale_price_rub: float = Field(..., examples=[500])

    quantity: int = Field(..., examples=[2])
    product_id: UUID = Field(..., examples=["b41f51ed-1969-461e-a966-7dd7d0752c9e"])

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class OfferSchema(_OfferBase):
    id: UUID
    offer_bitrix_id: str | None = Field(None, examples=["278495"])
    product: ProductSchema
    is_deleted: bool = Field(..., examples=[False])

    @computed_field
    @property
    def wholesale_price_rub(self) -> int:
        return int((self.price_rub + self.super_wholesale_price_rub) / 2)


class OfferPostSchema(_OfferBase):
    pass


class OfferPatchSchema(_OfferBase):
    pass
