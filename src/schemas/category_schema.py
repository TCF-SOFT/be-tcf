import json
from typing import Annotated, Any
from uuid import UUID

from fastapi import Form
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    computed_field,
    field_serializer,
    model_validator,
)
from slugify import slugify

from config import settings


class _CategoryBaseSchema(BaseModel):
    name: str = Field(..., examples=["Свечи"])

    model_config = ConfigDict(from_attributes=True)


class CategorySchema(_CategoryBaseSchema):
    id: UUID
    slug: str = Field(..., examples=["svechi-ford"])
    image_url: HttpUrl = Field(..., examples=[settings.IMAGE_PLACEHOLDER_URL])

    @field_serializer("image_url")
    def serialize_image_url(self, v):
        return str(v)


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

    @model_validator(mode="before")
    @classmethod
    def to_py_dict(cls, data: Any):
        """
        Transform the input data to a dictionary.
        """
        return json.loads(data)
