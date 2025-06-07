from uuid import UUID

from pydantic import (
    BaseModel,
    HttpUrl,
)


class CountSchema(BaseModel):
    count: int


class ImageSchema(BaseModel):
    id: UUID
    product_id: UUID
    image_url: HttpUrl
    is_thumbnail: bool
