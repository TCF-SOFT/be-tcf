import json
from typing import Any, Optional
from uuid import UUID

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


class _SubCategoryBase(BaseModel):
    name: str = Field(..., examples=["Свечи зажигания"])
    category_id: UUID = Field(..., examples=["2b3fb1a9-f13b-430f-a78e-94041fb0ed44"])
    image_url: Optional[HttpUrl] = Field(
        None, examples=["https://storage.yandexcloud.net/tcf-images/default.svg"]
    )

    @field_serializer("image_url")
    def serialize_image_url(self, v):
        return str(v) if v else None

    model_config = ConfigDict(from_attributes=True)


class SubCategorySchema(_SubCategoryBase):
    id: UUID
    slug: str = Field(..., examples=["svechi-zazhiganiia"])
    category_slug: str = Field(..., examples=["svechi-ford"])
    category_name: str = Field(..., examples=["Свечи"])


class SubCategoryPostSchema(_SubCategoryBase):
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
