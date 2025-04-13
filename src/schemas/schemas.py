from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, HttpUrl


class CountSchema(BaseModel):
    count: int


class ImageSchema(BaseModel):
    id: UUID
    product_id: UUID
    image_url: HttpUrl
    is_thumbnail: bool


class CategorySchema(BaseModel):
    id: UUID
    name: str
    slug: str
    image_url: Optional[HttpUrl] = None


class SubCategorySchema(BaseModel):
    id: UUID
    name: str
    slug: str
    category_id: UUID
    category_slug: str
    image_url: Optional[HttpUrl] = None


class ProductSchema(BaseModel):
    id: UUID
    bitrix_id: Optional[str] = None
    address_id: Optional[str] = None

    name: str
    brand: str
    manufacturer_number: Optional[str] = None
    cross_number: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None

    price_rub: Decimal
    super_wholesale_price_rub: Optional[Decimal] = None
    quantity: int

    sub_category_id: UUID
    sub_category_slug: str
    # images: list[ImageSchema] = []

    model_config = ConfigDict(from_attributes=True)


class ProductCreateSchema(BaseModel):
    bitrix_id: Optional[str] = None
    address_id: Optional[str] = None

    name: str
    brand: str
    manufacturer_number: Optional[str] = None
    cross_number: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None

    price_rub: Decimal
    super_wholesale_price_rub: Optional[Decimal] = None
    quantity: int

    sub_category_id: UUID
