from typing import Annotated
from uuid import UUID

from fastapi import Form
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    computed_field,
    field_validator,
)
from pydantic_core.core_schema import ValidationInfo

from config import settings
from src.schemas.product_schema import ProductSchema


class _OfferBase(BaseModel):
    sku: str | None = Field(None, examples=["AA-TEST"])
    brand: str = Field(..., examples=["MARKON"])
    manufacturer_number: str = Field(..., examples=["6000180"])

    internal_description: str | None = Field(
        None, examples=["Колодки тормозные передние"]
    )

    price_rub: float = Field(..., examples=[1000])
    super_wholesale_price_rub: float = Field(..., examples=[500])

    product_id: UUID = Field(..., examples=["b41f51ed-1969-461e-a966-7dd7d0752c9e"])

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class OfferSchema(_OfferBase):
    id: UUID
    offer_bitrix_id: str | None = Field(None, examples=["278495"])
    quantity: int = Field(..., examples=[2])
    product: ProductSchema
    is_deleted: bool = Field(..., examples=[False])

    image_url: HttpUrl | str = Field(..., examples=[settings.IMAGE_PLACEHOLDER_URL])

    @field_validator("image_url", mode="before")
    def _default_image(cls, v: HttpUrl | str, values: ValidationInfo) -> str:
        product: ProductSchema | None = values.data.get("product")
        fallback_image_url = product.image_url or settings.IMAGE_PLACEHOLDER_URL

        # TODO: discuss the default image logic (what should be a fallback)
        return v if v else fallback_image_url

    @computed_field
    @property
    def wholesale_price_rub(self) -> int:
        return int((self.price_rub + self.super_wholesale_price_rub) / 2)


class OfferPostSchema(_OfferBase):
    @classmethod
    def as_form(
        cls,
        sku: Annotated[str | None, Form(...)],
        brand: Annotated[str, Form(...)],
        manufacturer_number: Annotated[str, Form(...)],
        internal_description: Annotated[str | None, Form(...)],
        price_rub: Annotated[float, Form(...)],
        super_wholesale_price_rub: Annotated[float, Form(...)],
        product_id: Annotated[UUID, Form(...)],
    ) -> "OfferPostSchema":
        return cls(
            sku=sku,
            brand=brand,
            manufacturer_number=manufacturer_number,
            internal_description=internal_description,
            price_rub=price_rub,
            super_wholesale_price_rub=super_wholesale_price_rub,
            product_id=product_id,
        )


class OfferPatchSchema(_OfferBase):
    @classmethod
    def as_form(
        cls,
        sku: Annotated[str | None, Form(...)],
        brand: Annotated[str, Form(...)],
        manufacturer_number: Annotated[str, Form(...)],
        internal_description: Annotated[str | None, Form(...)],
        price_rub: Annotated[float, Form(...)],
        super_wholesale_price_rub: Annotated[float, Form(...)],
        product_id: Annotated[UUID, Form(...)],
    ) -> "OfferPatchSchema":
        return cls(
            sku=sku,
            brand=brand,
            manufacturer_number=manufacturer_number,
            internal_description=internal_description,
            price_rub=price_rub,
            super_wholesale_price_rub=super_wholesale_price_rub,
            product_id=product_id,
        )
