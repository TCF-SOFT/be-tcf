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
from slugify import slugify

from src.config import settings
from src.schemas.sub_category_schema import SubCategorySchema


class _ProductBase(BaseModel):
    name: str = Field(..., examples=["Колодки тормозные передние Escort 1990-2000"])
    cross_number: str | None = Field(
        None,
        examples=[
            "6962492, 1048310, 97AG2K021BA, 1133750, 1048308, 6180371, 94AB2K021AB, 6704271, 1130753"
        ],
    )
    sub_category_id: UUID = Field(
        ..., examples=["34805edd-26da-456b-8360-aee69bce5092"]
    )

    model_config = ConfigDict(from_attributes=True)


class ProductSchema(_ProductBase):
    id: UUID
    bitrix_id: str | None = Field(None, examples=["278495"])
    slug: str | None = None
    sub_category: SubCategorySchema

    is_deleted: bool = Field(..., examples=[False])

    image_url: HttpUrl = Field(..., examples=[settings.IMAGE_PLACEHOLDER_URL])

    @field_validator("image_url", mode="before")
    def _default_image(cls, v: str | None) -> str:
        return v if v else settings.IMAGE_PLACEHOLDER_URL


class ProductPostSchema(_ProductBase):
    # It is not visible in the API, in this case it is not necessary because slug is internal thing
    @computed_field
    @property
    def slug(self) -> str:
        return slugify(self.name, word_boundary=True, lowercase=False)

    @classmethod
    def as_form(
        cls,
        name: Annotated[str, Form(...)],
        cross_number: Annotated[str | None, Form(...)],
        sub_category_id: Annotated[UUID, Form(...)],
    ) -> "ProductPostSchema":
        return cls(
            name=name,
            cross_number=cross_number,
            sub_category_id=sub_category_id,
        )


class ProductPatchSchema(_ProductBase):
    @computed_field
    @property
    def slug(self) -> str:
        return slugify(self.name, word_boundary=True, lowercase=False)

    @classmethod
    def as_form(
        cls,
        name: Annotated[str, Form(...)],
        cross_number: Annotated[str | None, Form(...)],
        sub_category_id: Annotated[UUID, Form(...)],
    ) -> "ProductPatchSchema":
        return cls(
            name=name,
            cross_number=cross_number,
            sub_category_id=sub_category_id,
        )


class ProductAnalyticalSchema(BaseModel):
    name: str
    image_url: HttpUrl
    sold: int
    revenue: float
