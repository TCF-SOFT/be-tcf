from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProductSchema(BaseModel):
    id: UUID
    bitrix_id: Optional[str] = None
    address_id: Optional[str] = None

    category: str
    sub_category: str

    name: str
    brand: str
    manufacturer_number: Optional[str] = None
    cross_number: Optional[str] = None
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None

    price_rub: Decimal
    super_wholesale_price_rub: Optional[Decimal] = None
    quantity: int

    model_config = ConfigDict(from_attributes=True)
