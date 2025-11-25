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
from src.schemas.category_schema import CategorySchema


class _SubCategoryBase(BaseModel):
    name: str = Field(..., examples=["Свечи зажигания"])
    category_id: UUID

    model_config = ConfigDict(from_attributes=True)


class SubCategorySchema(_SubCategoryBase):
    id: UUID
    slug: str = Field(..., examples=["svechi-zazhiganiia"])
    image_url: HttpUrl = Field(..., examples=[settings.IMAGE_PLACEHOLDER_URL])

    category: CategorySchema

    @field_validator("image_url", mode="before")
    def _default_image(cls, v: str | None) -> str:
        return v if v else settings.IMAGE_PLACEHOLDER_URL


class SubCategoryPostSchema(_SubCategoryBase):
    @computed_field
    @property
    def slug(self) -> str:
        return slugify(self.name, word_boundary=True, lowercase=True)

    @classmethod
    def as_form(
        cls,
        name: Annotated[str, Form(...)],
        category_id: Annotated[UUID, Form(...)],
    ) -> "SubCategoryPostSchema":
        return cls(
            name=name,
            category_id=category_id,
        )


class SubCategoryPutSchema(_SubCategoryBase):
    @computed_field
    @property
    def slug(self) -> str:
        return slugify(self.name, word_boundary=True, lowercase=True)

    @classmethod
    def as_form(
        cls,
        name: Annotated[str, Form(...)],
        category_id: Annotated[UUID, Form(...)],
    ) -> "SubCategoryPutSchema":
        return cls(
            name=name,
            category_id=category_id,
        )
