from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class WaybillOfferPostSchema(BaseModel):
    offer_id: UUID
    quantity: int
    brand: str = Field(..., min_length=1)
    manufacturer_number: str | None
    price_rub: Decimal
    