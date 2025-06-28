from typing import Optional

from sqlalchemy import (
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, uuid_pk


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
