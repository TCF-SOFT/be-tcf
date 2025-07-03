import uuid

from sqlalchemy import (
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, uuid_pk


class SubCategory(Base):
    __tablename__ = "sub_categories"

    id: Mapped[uuid_pk]
    name: Mapped[str] = mapped_column(String, nullable=False)
    slug: Mapped[str] = mapped_column(String, nullable=False)
    image_url: Mapped[str | None] = mapped_column(String, nullable=True)

    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("categories.id"))

    # Relationships
    category = relationship("Category", back_populates="sub_categories", lazy="joined")
    products = relationship("Product", back_populates="sub_category")

    @property
    def category_slug(self) -> str:
        return self.category.slug

    @property
    def category_name(self) -> str:
        return self.category.name

    # Constraints
    __table_args__ = (UniqueConstraint("slug", name="sub_categories_slug_key"),)
