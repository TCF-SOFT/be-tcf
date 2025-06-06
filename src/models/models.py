import uuid
from typing import Literal, Optional

from sqlalchemy import (
    Boolean,
    ForeignKey,
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

    # Relationships
    waybills = relationship("Waybill", back_populates="user", lazy="joined")

    def __str__(self):
        return f"User: {self.email}"


class Offer(Base):
    id: Mapped[uuid_pk]
    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("products.id"), nullable=False
    )
    offer_bitrix_id: Mapped[str] = mapped_column(String, nullable=True)

    brand: Mapped[str] = mapped_column(String, nullable=False)
    manufacturer_number: Mapped[str] = mapped_column(String, nullable=True)
    internal_description: Mapped[str] = mapped_column(Text, nullable=True)

    price_rub: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False)
    super_wholesale_price_rub: Mapped[float] = mapped_column(
        Numeric(12, 4), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    # Soft delete field
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    product = relationship("Product", back_populates="offers", lazy="joined")
    waybill_offers = relationship("WaybillOffer", back_populates="offer")

    # <-- Pydantic tiny helpers ------------------------------
    @property
    def image_url(self) -> Optional[str]:
        """Proxy `product.image_url` so Pydantic can see it."""
        return self.product.image_url if self.product else None

    @property
    def sub_category_slug(self) -> str:
        return self.product.sub_category_slug

    @property
    def category_slug(self) -> str:
        return self.product.sub_category.category_slug

    @property
    def product_name(self) -> str:
        return self.product.name

    @property
    def cross_number(self) -> Optional[str]:
        """
        Proxy `product.cross_number` so Pydantic can see it.
        """
        return self.product.cross_number if self.product else None

    # --------------------------------------------------------


class Product(Base):
    id: Mapped[uuid_pk]
    bitrix_id: Mapped[str] = mapped_column(String, nullable=True)
    address_id: Mapped[str] = mapped_column(String, nullable=True)

    sub_category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sub_categories.id"), nullable=False
    )

    name: Mapped[str] = mapped_column(String, nullable=False)
    slug: Mapped[str] = mapped_column(String, nullable=True)
    cross_number: Mapped[str] = mapped_column(String, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    image_url: Mapped[str] = mapped_column(String, nullable=True)

    # Soft delete field
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    sub_category = relationship("SubCategory", back_populates="products", lazy="joined")
    offers = relationship("Offer", back_populates="product", lazy="select")

    # Pydantic Proxies
    @property
    def sub_category_slug(self) -> str:
        return self.sub_category.slug

    @property
    def category_slug(self) -> str:
        return self.sub_category.category_slug

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

    # Relationships
    category = relationship("Category", back_populates="sub_categories", lazy="joined")
    products = relationship("Product", back_populates="sub_category")

    @property
    def category_slug(self) -> str:
        """
        Proxy `category.slug` so Pydantic can see it.
        """
        return self.category.slug if self.category else None

    # Constraints
    __table_args__ = (UniqueConstraint("slug", name="sub_categories_slug_key"),)

    def __str__(self):
        return f"SubCategory: {self.name}"


class Waybill(Base):
    id: Mapped[uuid_pk]
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    waybill_type: Mapped[Literal["WAYBILL_IN", "WAYBILL_OUT", "WAYBILL_RETURN"]] = mapped_column(
        String, nullable=False
    )
    is_pending: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    counterparty_name: Mapped[str] = mapped_column(String, nullable=False)

    # Relationships
    user = relationship("User", back_populates="waybills", lazy="joined")
    waybill_offers = relationship(
        "WaybillOffer", back_populates="waybill", lazy="joined"
    )

    @property
    def author(self) -> str:
        """
        Proxy `user.name` so Pydantic can see it.
        """
        return self.user.first_name


class StockMovement(Base):
    id: Mapped[uuid_pk]

    offer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("offers.id"), nullable=False)
    waybill_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("waybills.id"), nullable=True
    )

    waybill_type: Mapped[Literal["WAYBILL_IN", "WAYBILL_OUT", "WAYBILL_RETURN"]] = mapped_column(
        String, nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    comment: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    reverted: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    offer = relationship("Offer", lazy="joined")
    user = relationship("User", lazy="joined")
    waybill = relationship("Waybill", lazy="joined")


class WaybillOffer(Base):
    """
    Визуальное отображение того, что пользователь выбрал на момент оформления.
     Это как бумажная накладная — она не меняется даже если продукт позже удалён или переименован.
    """

    id: Mapped[uuid_pk]
    waybill_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("waybills.id"), nullable=False
    )
    offer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("offers.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    # Snapshot fields
    brand: Mapped[str] = mapped_column(String, nullable=False)
    manufacturer_number: Mapped[str] = mapped_column(String, nullable=True)
    price_rub: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False)

    # Relationships
    waybill = relationship("Waybill", back_populates="waybill_offers", lazy="joined")
    offer = relationship("Offer", back_populates="waybill_offers", lazy="joined")
