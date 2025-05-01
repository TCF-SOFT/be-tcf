from typing import Optional
from uuid import UUID

from fastapi import UploadFile, File
from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    computed_field,
    field_serializer,
)
from slugify import slugify


class _CategoryBaseSchema(BaseModel):
    name: str = Field(..., examples=["Свечи"])
    image_url: Optional[HttpUrl] = Field(
        None, examples=["https://chibisafe.eucalytics.uk//REXA2bZVWeZT.webp"]
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


class CategoryPutSchema(_CategoryBaseSchema):
    pass
