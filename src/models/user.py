from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    String,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, str_uniq, uuid_pk
from src.schemas.common.enums import CustomerType, Role, ShippingMethod

if TYPE_CHECKING:
    from src.models.address import Address
    from src.models.cart import Cart
    from src.models.order import Order
    from src.models.waybill import Waybill


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid_pk]
    clerk_id: Mapped[str] = mapped_column(String, nullable=True, unique=True)
    email: Mapped[str_uniq]

    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    role: Mapped[Role] = mapped_column(
        SQLEnum(Role, native_enum=False),
        nullable=False,
        default=Role.USER,
    )

    # --------------------------------------------------
    #      Customer Only Fields - Public Metadata
    # --------------------------------------------------
    customer_type: Mapped[CustomerType] = mapped_column(
        SQLEnum(CustomerType, native_enum=False),
        nullable=False,
        default=CustomerType.USER_RETAIL,
    )

    mailing: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    phone: Mapped[str | None] = mapped_column(String, nullable=True)
    city: Mapped[str | None] = mapped_column(String, nullable=True)
    note: Mapped[str | None] = mapped_column(String, nullable=True)

    shipping_method: Mapped[ShippingMethod | None] = mapped_column(
        SQLEnum(ShippingMethod, native_enum=False),
        default=None,
        nullable=True,
    )
    shipping_company: Mapped[str | None] = mapped_column(String, nullable=True)

    # Relationships
    created_waybills: Mapped[list["Waybill"]] = relationship(
        "Waybill", foreign_keys="Waybill.author_id", back_populates="author"
    )
    received_waybills: Mapped[list["Waybill"]] = relationship(
        "Waybill", foreign_keys="Waybill.customer_id", back_populates="customer"
    )
    addresses: Mapped[list["Address"]] = relationship(
        "Address", back_populates="user", lazy="select"
    )
    orders: Mapped[list["Order"]] = relationship(
        "Order", back_populates="user", lazy="select"
    )
    carts: Mapped[list["Cart"]] = relationship(
        "Cart", back_populates="user", lazy="select"
    )
