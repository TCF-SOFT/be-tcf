from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    computed_field,
)

from src.config import settings


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
    category_slug: str = Field(..., examples=["svechi-ford"])
    category_name: str = Field(..., examples=["Свечи"])
    sub_category_slug: str = Field(..., examples=["svechi-zazhiganiia"])
    sub_category_name: str = Field(..., examples=["Свечи зажигания"])
    product_name: str = Field(..., examples=["Escort 1990-2000"])
    cross_number: str | None = Field(
        None,
        examples=[
            "6962492, 1048310, 97AG2K021BA, 1133750, 1048308, 6180371, 94AB2K021AB, 6704271, 1130753"
        ],
    )
    image_url: HttpUrl = Field(..., examples=[settings.IMAGE_PLACEHOLDER_URL])
    is_deleted: bool = Field(..., examples=[False])

    @computed_field
    @property
    def wholesale_price_rub(self) -> int:
        return int((self.price_rub + self.super_wholesale_price_rub) / 2)


class OfferPostSchema(_OfferBase):
    pass


class OfferPutSchema(_OfferBase):
    pass
