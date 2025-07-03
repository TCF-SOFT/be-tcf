from typing import Annotated
from uuid import UUID

from fastapi import Form
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
)
from slugify import slugify

from config import settings


class _CategoryBaseSchema(BaseModel):
    name: str = Field(..., examples=["Свечи"])

    model_config = ConfigDict(from_attributes=True)


class CategorySchema(_CategoryBaseSchema):
    id: UUID
    slug: str = Field(..., examples=["svechi-ford"])
    image_url: str = Field(..., examples=[settings.IMAGE_PLACEHOLDER_URL])


class CategoryPostSchema(_CategoryBaseSchema):
    @computed_field
    @property
    def slug(self) -> str:
        return slugify(self.name, word_boundary=True, lowercase=True)

    @classmethod
    def as_form(cls, name: Annotated[str, Form(...)]) -> "CategoryPostSchema":
        return cls(name=name)


class CategoryPutSchema(_CategoryBaseSchema):
    @computed_field
    @property
    def slug(self) -> str:
        return slugify(self.name, word_boundary=True, lowercase=True)

    @classmethod
    def as_form(cls, name: Annotated[str, Form(...)]) -> "CategoryPutSchema":
        return cls(name=name)
