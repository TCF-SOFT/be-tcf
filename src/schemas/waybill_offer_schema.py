from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.offer_schema import OfferSchema


class _WaybillOfferBaseSchema(BaseModel):
    offer_id: UUID
    brand: str = Field(..., min_length=1, examples=["BSG"])
    manufacturer_number: str = Field(..., min_length=1, examples=["BSG-12345"])
    quantity: int = Field(..., gt=0, examples=[10])
    price_rub: float = Field(..., examples=[1000])

    model_config = ConfigDict(from_attributes=True)


class WaybillOfferSchema(_WaybillOfferBaseSchema):
    id: UUID
    waybill_id: UUID
    offer: OfferSchema


class WaybillOfferPostSchema(_WaybillOfferBaseSchema):
    pass


class WaybillOfferPatchSchema(_WaybillOfferBaseSchema):
    pass
