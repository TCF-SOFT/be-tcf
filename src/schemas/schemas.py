from decimal import Decimal
from typing import Literal, Optional
from uuid import UUID, uuid4
from slugify import slugify

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, computed_field


class CountSchema(BaseModel):
    count: int


class ImageSchema(BaseModel):
    id: UUID
    product_id: UUID
    image_url: HttpUrl
    is_thumbnail: bool


class UserSchema(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    hashed_password: str
    first_name: str
    last_name: Optional[str] = None
    avatar_url: Optional[HttpUrl] = None
    email: str
    is_active: bool
    is_superuser: bool
    is_verified: bool
    role: Literal["admin", "employee", "user"]
    position: Optional[Literal["Менеджер", "Кладовщик"]] = None

    model_config = ConfigDict(from_attributes=True)


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
    seo_name: str
    brand: str
    slug: Optional[str] = None
    manufacturer_number: Optional[str] = None
    cross_number: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None

    price_rub: float
    super_wholesale_price_rub: Optional[Decimal] = None
    quantity: int

    sub_category_id: UUID
    sub_category_slug: str
    # images: list[ImageSchema] = []

    model_config = ConfigDict(from_attributes=True)


class ProductPostSchema(BaseModel):
    bitrix_id: Optional[str] = None
    address_id: Optional[str] = None

    name: str
    # seo_name: str
    brand: str
    # slug: Optional[str] = None

    manufacturer_number: Optional[str] = None
    cross_number: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None

    price_rub: Decimal
    super_wholesale_price_rub: Optional[Decimal] = None
    quantity: int

    sub_category_id: UUID = Field(..., examples=["34805edd-26da-456b-8360-aee69bce5092"])
    sub_category_slug: str = Field(..., examples=["podkrylki"])

    # It is not visible in the API, in this case it is not necessary because slug is internal thing
    @computed_field(alias="seo_name")
    @property
    def seo_name(self) -> str:
        return slugify(self.name, word_boundary=True, lowercase=True)

    @computed_field
    @property
    def slug(self) -> str:
        return slugify(self.name, word_boundary=True, lowercase=True)
