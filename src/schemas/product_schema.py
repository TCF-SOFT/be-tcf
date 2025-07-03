from typing import Annotated
from uuid import UUID

from fastapi import Form
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    computed_field,
    field_serializer,
)
from slugify import slugify

from config import settings


class _ProductBase(BaseModel):
    name: str = Field(..., examples=["Колодки тормозные передние Escort 1990-2000"])
    cross_number: str | None = Field(
        None,
        examples=[
            "6962492, 1048310, 97AG2K021BA, 1133750, 1048308, 6180371, 94AB2K021AB, 6704271, 1130753"
        ],
    )
    description: str | None = Field(None, examples=["Колодки тормозные передние"])

    sub_category_id: UUID = Field(
        ..., examples=["34805edd-26da-456b-8360-aee69bce5092"]
    )

    model_config = ConfigDict(from_attributes=True)


class ProductSchema(_ProductBase):
    id: UUID
    bitrix_id: str | None = Field(None, examples=["278495"])
    slug: str | None = None
    category_slug: str = Field(..., examples=["svechi-ford"])
    category_name: str = Field(..., examples=["Свечи"])
    sub_category_slug: str = Field(..., examples=["svechi-zazhiganiia"])
    sub_category_name: str = Field(..., examples=["Свечи зажигания"])

    is_deleted: bool = Field(..., examples=[False])

    image_url: HttpUrl

    @field_serializer("image_url")
    def serialize_image_url(self, v):
        return str(v or settings.IMAGE_PLACEHOLDER_URL)


class ProductPostSchema(_ProductBase):
    # It is not visible in the API, in this case it is not necessary because slug is internal thing
    @computed_field
    @property
    def slug(self) -> str:
        return slugify(self.name, word_boundary=True, lowercase=True)

    @classmethod
    def as_form(
        cls,
        name: Annotated[str, Form(...)],
        cross_number: Annotated[str | None, Form(...)],
        description: Annotated[str | None, Form(...)],
        sub_category_id: Annotated[UUID, Form(...)],
    ) -> "ProductPostSchema":
        return cls(
            name=name,
            cross_number=cross_number,
            description=description,
            sub_category_id=sub_category_id,
        )


class ProductPutSchema(_ProductBase):
    @computed_field
    @property
    def slug(self) -> str:
        return slugify(self.name, word_boundary=True, lowercase=True)

    @classmethod
    def as_form(
        cls,
        name: Annotated[str, Form(...)],
        cross_number: Annotated[str | None, Form(...)],
        description: Annotated[str | None, Form(...)],
        sub_category_id: Annotated[UUID, Form(...)],
    ) -> "ProductPutSchema":
        return cls(
            name=name,
            cross_number=cross_number,
            description=description,
            sub_category_id=sub_category_id,
        )
