from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class _OrderOfferBaseSchema(BaseModel):
    offer_id: UUID
    quantity: int = Field(..., gt=0, examples=[10])
    brand: str = Field(..., min_length=1, examples=["BSG"])
    manufacturer_number: str = Field(..., min_length=1, examples=["BSG-12345"])
    price_rub: float = Field(..., examples=[1000])

    model_config = ConfigDict(from_attributes=True)


class OrderOfferSchema(_OrderOfferBaseSchema):
    id: UUID
    order_id: UUID
    product_name: str
    address_id: str | None = Field(None, examples=["AA-TEST"])
    image_url: str | None
    category_slug: str = Field(..., examples=["svechi-ford"])
    category_name: str = Field(..., examples=["Свечи"])
    sub_category_slug: str = Field(..., examples=["svechi-zazhiganiia"])
    sub_category_name: str = Field(..., examples=["Свечи зажигания"])
    product_id: UUID


class OrderOfferPostSchema(_OrderOfferBaseSchema):
    pass
