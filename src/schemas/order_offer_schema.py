from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.offer_schema import OfferSchema


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
    offer: OfferSchema


class OrderOfferPostSchema(_OrderOfferBaseSchema):
    pass


class OrderOfferPutSchema(_OrderOfferBaseSchema):
    pass
