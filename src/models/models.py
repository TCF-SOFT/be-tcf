import uuid
from typing import Literal, Optional

import sqlalchemy.sql
from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, Text, Numeric, Index
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, str_uniq, uuid_pk


class User(Base):
    id: Mapped[uuid_pk]
    email: Mapped[str_uniq]
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    role: Mapped[Literal["admin", "user"]] = mapped_column(
        String, nullable=False, default="user"
    )

    def __str__(self):
        return f"User: {self.email}"



class Product(Base):
    id: Mapped[uuid_pk]
    bitrix_id: Mapped[str] = mapped_column(String, nullable=True)
    address_id:  Mapped[str] = mapped_column(String, nullable=True)

    category: Mapped[str] = mapped_column(String, nullable=False)
    sub_category: Mapped[str] = mapped_column(String, nullable=False)

    name: Mapped[str] = mapped_column(String, nullable=False)
    brand: Mapped[str] = mapped_column(String, nullable=False)
    manufacturer_number: Mapped[str] = mapped_column(String, nullable=True)
    cross_number: Mapped[str] = mapped_column(String, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    thumbnail_url: Mapped[str] = mapped_column(String, nullable=True)

    price_rub: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False)
    super_wholesale_price_rub: Mapped[float] = mapped_column(Numeric(12, 4), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    search_vector: Mapped[str] = mapped_column(
        TSVECTOR
    )

    __table_args__ = (
        Index('search_vector_idx', 'search_vector', postgresql_using='gin'),
    )

    # Ассоциация с таблицей Image (1 product -> M images)
    # Using 'selectin' loading to efficiently load images in a separate query immediately after the main query
    # check readme for more info
    images = relationship(
        "Image",
        back_populates="product",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __str__(self):
        return f"Product: {self.name}"


class Image(Base):
    id: Mapped[uuid_pk]
    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("products.id"), nullable=False
    )
    image_url: Mapped[str] = mapped_column(String, nullable=True)
    is_thumbnail: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    product = relationship("Product", back_populates="images", lazy="select")

    def __str__(self):
        return f"Image: {self.image_url}"

