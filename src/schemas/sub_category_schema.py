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

from src.config import settings


class _SubCategoryBase(BaseModel):
    name: str = Field(..., examples=["Свечи зажигания"])
    category_id: UUID = Field(..., examples=["2b3fb1a9-f13b-430f-a78e-94041fb0ed44"])

    model_config = ConfigDict(from_attributes=True)


class SubCategorySchema(_SubCategoryBase):
    id: UUID
    slug: str = Field(..., examples=["svechi-zazhiganiia"])
    category_slug: str = Field(..., examples=["svechi-ford"])
    category_name: str = Field(..., examples=["Свечи"])

    image_url: HttpUrl | None = Field(settings.IMAGE_PLACEHOLDER_URL)

    @field_serializer("image_url")
    def serialize_image_url(self, v):
        return str(v)


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

    @model_validator(mode="before")
    @classmethod
    def to_py_dict(cls, data: Any):
        """
        Transform the input data to a dictionary.
        """
        return json.loads(data)
