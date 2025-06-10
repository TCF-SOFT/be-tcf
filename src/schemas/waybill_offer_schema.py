from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class _WaybillOfferBaseSchema(BaseModel):
    offer_id: UUID
    quantity: int = Field(..., gt=0, examples=[10])
    brand: str = Field(..., min_length=1, examples=["BSG"])
    manufacturer_number: str = Field(..., min_length=1, examples=["BSG-12345"])
    price_rub: float = Field(..., examples=[1000])

    model_config = ConfigDict(from_attributes=True)


class WaybillOfferPostSchema(_WaybillOfferBaseSchema):
    pass


class WaybillOfferSchema(_WaybillOfferBaseSchema):
    id: UUID
    waybill_id: UUID
    product_name: str
    address_id: str | None = Field(None, examples=["AA-TEST"])
    image_url: str | None
    category_slug: str
    sub_category_slug: str
