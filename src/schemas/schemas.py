from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, HttpUrl


class ImageSchema(BaseModel):
    id: UUID
    product_id: UUID
    image_url: HttpUrl
    is_thumbnail: bool


class CategorySchema(BaseModel):
    id: UUID
    name: str
    image_url: Optional[HttpUrl] = None


class SubCategorySchema(BaseModel):
    id: UUID
    name: str
    category_id: UUID


class ProductSchema(BaseModel):
    id: UUID
    bitrix_id: Optional[str] = None
    address_id: Optional[str] = None

    name: str
    brand: str
    manufacturer_number: Optional[str] = None
    cross_number: Optional[str] = None
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None

    price_rub: Decimal
    super_wholesale_price_rub: Optional[Decimal] = None
    quantity: int

    sub_category_id: UUID
    image: Optional[ImageSchema] = None

    model_config = ConfigDict(from_attributes=True)


class ProductCreateSchema(BaseModel):
    bitrix_id: Optional[str] = None
    address_id: Optional[str] = None

    name: str
    brand: str
    manufacturer_number: Optional[str] = None
    cross_number: Optional[str] = None
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None

    price_rub: Decimal
    super_wholesale_price_rub: Optional[Decimal] = None
    quantity: int

    sub_category_id: UUID
