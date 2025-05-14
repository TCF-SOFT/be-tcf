import uuid
from typing import Literal, Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Boolean,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, str_uniq, uuid_pk


class User(Base):
    id: Mapped[uuid_pk]
    email: Mapped[str_uniq]
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    role: Mapped[Literal["admin", "employee", "user"]] = mapped_column(
        String, nullable=False, default="user"
    )

    position: Mapped[Literal["Менеджер", "Кладовщик"]] = mapped_column(
        String, nullable=True
    )

    def __str__(self):
        return f"User: {self.email}"

class Offer(Base):
    id: Mapped[uuid_pk]
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id"), nullable=False)
    offer_bitrix_id: Mapped[str] = mapped_column(String, nullable=True)

    brand: Mapped[str] = mapped_column(String, nullable=False)
    manufacturer_number: Mapped[str] = mapped_column(String, nullable=True)
    internal_description: Mapped[str] = mapped_column(Text, nullable=True)

    price_rub: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False)
    super_wholesale_price_rub: Mapped[float] = mapped_column(
        Numeric(12, 4), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    product = relationship("Product", back_populates="offers", lazy="joined")


class Product(Base):
    id: Mapped[uuid_pk]
    bitrix_id: Mapped[str] = mapped_column(String, nullable=True)
    address_id: Mapped[str] = mapped_column(String, nullable=True)

    sub_category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sub_categories.id"), nullable=False
    )
    sub_category_slug: Mapped[str] = mapped_column(String, nullable=False)

    name: Mapped[str] = mapped_column(String, nullable=False)
    slug: Mapped[str] = mapped_column(String, nullable=True)
    cross_number: Mapped[str] = mapped_column(String, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    image_url: Mapped[str] = mapped_column(String, nullable=True)

    # Relationships
    sub_category = relationship("SubCategory", back_populates="products", lazy="joined")
    offers = relationship("Offer", back_populates="product", lazy="select")

    # Vector search
    # embedding: Mapped[Vector] = mapped_column(Vector(1536), nullable=True)

    # Constraints
    __table_args__ = (
        UniqueConstraint("slug", name="products_slug_key"),
        # Index(
        #     "idx_products_embedding",
        #     "embedding",
        #     postgresql_using="hnsw",
        #     postgresql_with={"m": 16, "ef_construction": 64},
        #     postgresql_ops={"embedding": "vector_l2_ops"},
        # ),
    )

    def __str__(self):
        return f"Product: {self.name}"


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[uuid_pk]
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String, nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Relationships
    sub_categories = relationship(
        "SubCategory", back_populates="category", cascade="all, delete-orphan"
    )

    # Constraints
    __table_args__ = (UniqueConstraint("slug", name="categories_slug_key"),)

    def __str__(self):
        return f"Category: {self.name}"


class SubCategory(Base):
    __tablename__ = "sub_categories"

    id: Mapped[uuid_pk]
    name: Mapped[str] = mapped_column(String, nullable=False)
    slug: Mapped[str] = mapped_column(String, nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("categories.id"))
    category_slug: Mapped[str] = mapped_column(String, nullable=False)

    # Relationships
    category = relationship("Category", back_populates="sub_categories")
    products = relationship("Product", back_populates="sub_category")

    # Constraints
    __table_args__ = (UniqueConstraint("slug", name="sub_categories_slug_key"),)

    def __str__(self):
        return f"SubCategory: {self.name}"


# class Image(Base):
#     id: Mapped[uuid_pk]
#     product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id"))
#     image_url: Mapped[str] = mapped_column(String, nullable=False)
#     is_thumbnail: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
#
#     product = relationship("Product", back_populates="images", lazy="select")
#
#     def __str__(self):
#         return f"Image: {self.image_url}"
