from typing import Literal, Optional
from uuid import UUID, uuid4

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
)


class CountSchema(BaseModel):
    count: int


class ImageSchema(BaseModel):
    id: UUID
    product_id: UUID
    image_url: HttpUrl
    is_thumbnail: bool


class UserSchema(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    hashed_password: str
    first_name: str
    last_name: Optional[str] = None
    avatar_url: Optional[HttpUrl] = Field(
        None, examples=["https://chibisafe.eucalytics.uk//REXA2bZVWeZT.webp"]
    )
    email: str
    is_active: bool
    is_superuser: bool
    is_verified: bool
    role: Literal["admin", "employee", "user"]
    position: Optional[Literal["Менеджер", "Кладовщик"]] = None

    model_config = ConfigDict(from_attributes=True)
