import uuid

from sqlalchemy import (
    Boolean,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, uuid_pk


class Product(Base):
    id: Mapped[uuid_pk]
    bitrix_id: Mapped[str] = mapped_column(String, nullable=True)

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
