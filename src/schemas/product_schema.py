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


class _ProductBase(BaseModel):
    name: str = Field(..., examples=["Колодки тормозные передние Escort 1990-2000"])
    cross_number: Optional[str] = Field(
        None,
        examples=[
            "6962492, 1048310, 97AG2K021BA, 1133750, 1048308, 6180371, 94AB2K021AB, 6704271, 1130753"
        ],
    )
    description: Optional[str] = Field(None, examples=["Колодки тормозные передние"])
    image_url: Optional[HttpUrl] = Field(
        None, examples=["https://storage.yandexcloud.net/tcf-images/default.svg"]
    )
    sub_category_id: UUID = Field(
        ..., examples=["34805edd-26da-456b-8360-aee69bce5092"]
    )

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("image_url")
    def serialize_image_url(self, v):
        return str(v) if v else None


class ProductSchema(_ProductBase):
    id: UUID
    bitrix_id: Optional[str] = Field(None, examples=["278495"])
    slug: Optional[str] = None
    category_slug: str = Field(..., examples=["svechi-ford"])
    category_name: str = Field(..., examples=["Свечи"])
    sub_category_slug: str = Field(..., examples=["svechi-zazhiganiia"])
    sub_category_name: str = Field(..., examples=["Свечи зажигания"])

    is_deleted: bool = Field(..., examples=[False])


class ProductPostSchema(_ProductBase):
    # It is not visible in the API, in this case it is not necessary because slug is internal thing
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


class ProductPutSchema(_ProductBase):
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
