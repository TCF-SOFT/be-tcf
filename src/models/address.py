from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, uuid_pk
from src.schemas.common.enums import ShippingMethod

if TYPE_CHECKING:
    from src.models.order import Order
    from src.models.user import User


class Address(Base):
    __tablename__ = "addresses"

    id: Mapped[uuid_pk]
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str] = mapped_column(String, nullable=True)

    city: Mapped[str] = mapped_column(String, nullable=False)
    street: Mapped[str] = mapped_column(String, nullable=False)
    postal_code: Mapped[str] = mapped_column(String, nullable=False)

    shipping_method: Mapped[ShippingMethod] = mapped_column(
        SQLEnum(ShippingMethod, native_enum=False),
        default=ShippingMethod.OTHER,
        nullable=False,
    )
    shipping_company: Mapped[str | None] = mapped_column(String, nullable=True)

    is_default: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(
        "User", back_populates="addresses", lazy="joined"
    )
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="address")
