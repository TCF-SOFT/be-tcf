from typing import Optional
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    computed_field,
    field_serializer,
)
from slugify import slugify


class _ProductBase(BaseModel):
    address_id: Optional[str] = Field(None, examples=["AA-TEST"])

    name: str = Field(..., examples=["Колодки тормозные передние Escort 1990-2000"])
    brand: str = Field(..., examples=["MARKON"])
    manufacturer_number: Optional[str] = Field(None, examples=["6000180"])
    cross_number: Optional[str] = Field(
        None,
        examples=[
            "6962492, 1048310, 97AG2K021BA, 1133750, 1048308, 6180371, 94AB2K021AB, 6704271, 1130753"
        ],
    )
    description: Optional[str] = Field(None, examples=["Колодки тормозные передние"])
    image_url: Optional[HttpUrl] = Field(
        None, examples=["https://chibisafe.eucalytics.uk//REXA2bZVWeZT.webp"]
    )

    price_rub: float = Field(..., examples=[578.8])
    super_wholesale_price_rub: float | None = Field(None, examples=[579.00])
    quantity: int = Field(..., examples=[2])

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("image_url")
    def serialize_image_url(self, v):
        return str(v) if v else None


class ProductSchema(_ProductBase):
    id: UUID
    bitrix_id: Optional[str] = Field(None, examples=["278495"])

    seo_name: str
    slug: Optional[str] = None

    sub_category_id: UUID = Field(
        ..., examples=["917e7aab-d859-4e2d-84bf-9a1c844e428e"]
    )
    sub_category_slug: str = Field(..., examples=["kolodki-tormoznye-diskovye"])


class ProductPostSchema(_ProductBase):
    # seo_name: str
    # slug: Optional[str] = None

    sub_category_id: UUID = Field(
        ..., examples=["34805edd-26da-456b-8360-aee69bce5092"]
    )
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


class ProductPutSchema(_ProductBase):
    pass
