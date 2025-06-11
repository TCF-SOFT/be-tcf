import uuid
from typing import Literal

from fastapi_users import schemas
from pydantic import BaseModel, Field, HttpUrl, field_serializer


class _BaseUser(BaseModel):
    first_name: str = Field(..., examples=["Vasilii"])
    last_name: str | None = Field(None, examples=["Pinov"])
    role: Literal["admin", "employee", "user"] = Field("user", examples=["user"])
    position: Literal["Менеджер", "Кладовщик"] | None = Field(
        None, examples=["Менеджер"]
    )
    avatar_url: HttpUrl | None = Field(
        None, examples=["https://storage.yandexcloud.net/tcf-images/default.svg"]
    )

    # Customer only fields:
    customer_type: Literal["retail", "wholesale", "super_wholesale"] = Field(
        "retail", examples=["retail"]
    )
    mailing: bool = False

    @field_serializer("avatar_url")
    def serialize_avatar_url(self, v):
        return str(v) if v else None


class UserRead(schemas.BaseUser[uuid.UUID], _BaseUser):
    pass


class UserCreate(schemas.BaseUserCreate, _BaseUser):
    pass


class UserUpdate(schemas.BaseUserUpdate, _BaseUser):
    pass
