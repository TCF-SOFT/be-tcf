import json
from typing import Any, Optional
from uuid import UUID

from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    computed_field,
    field_serializer,
    model_validator,
    field_validator,
)
from pydantic_core.core_schema import ValidationInfo
from slugify import slugify


class _CategoryBaseSchema(BaseModel):
    name: str = Field(..., examples=["Свечи"])
    image_url: Optional[HttpUrl] = Field(
        None, examples=["https://storage.yandexcloud.net/tcf-images/default.svg"]
    )

    @field_serializer("image_url")
    def serialize_image_url(self, v):
        return str(v) if v else None


class CategorySchema(_CategoryBaseSchema):
    id: UUID
    slug: str = Field(..., examples=["svechi-ford"])


class CategoryPostSchema(_CategoryBaseSchema):
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


class CategoryPatchSchema(BaseModel):
    name: str | None = Field(None, examples=["Свечи"])
    image_url: HttpUrl | None = Field(
        None, examples=["https://storage.yandexcloud.net/tcf-images/default.svg"]
    )
    slug: str | None = Field(None, examples=["svechi-ford"])

    @model_validator(mode="before")
    @classmethod
    def to_py_dict(cls, data: Any):
        """
        Transform the input data to a dictionary.
        """
        return json.loads(data)

    @model_validator(mode="after")
    def generate_slug(self) -> "CategoryPatchSchema":
        if not self.slug and self.name:
            self.slug = slugify(self.name, word_boundary=True, lowercase=True)
        return self
