from typing import TYPE_CHECKING

from fastapi_users_db_sqlalchemy import (
    SQLAlchemyBaseUserTableUUID,
    SQLAlchemyUserDatabase,
)
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
    # Do not import, just use type with `session: "AsyncSession"`
    from sqlalchemy.ext.asyncio import AsyncSession

    from src.models.address import Address
    from src.models.cart import Cart
    from src.models.order import Order
    from src.models.waybill import Waybill


class User(Base, SQLAlchemyBaseUserTableUUID):
    __tablename__ = "users"

    id: Mapped[uuid_pk]
    email: Mapped[str_uniq]
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    role: Mapped[Role] = mapped_column(
        SQLEnum(Role, native_enum=False),
        nullable=False,
        default=Role.USER,
    )

    # --------------------------------------------------
    #            Customer Only Fields
    # --------------------------------------------------
    customer_type: Mapped[CustomerType] = mapped_column(
        SQLEnum(CustomerType, native_enum=False),
        nullable=False,
        default=CustomerType.USER_RETAIL,
    )

    mailing: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    phone: Mapped[str | None] = mapped_column(String, nullable=True)
    city: Mapped[str | None] = mapped_column(String, nullable=True)
    notes: Mapped[str | None] = mapped_column(String, nullable=True)

    shipping_method: Mapped[ShippingMethod | None] = mapped_column(
        SQLEnum(ShippingMethod, native_enum=False),
        default=None,
        nullable=True,
    )
    shipping_company: Mapped[str | None] = mapped_column(String, nullable=True)

    # Relationships
    waybills: Mapped[list["Waybill"]] = relationship(
        "Waybill", back_populates="user", lazy="joined"
    )
    addresses: Mapped[list["Address"]] = relationship(
        "Address", back_populates="user", lazy="joined"
    )
    orders: Mapped[list["Order"]] = relationship(
        "Order", back_populates="user", lazy="joined"
    )
    carts: Mapped[list["Cart"]] = relationship(
        "Cart", back_populates="user", lazy="joined"
    )

    @classmethod
    def get_db(cls, session: "AsyncSession"):
        """
        Database Adapter
        """
        return SQLAlchemyUserDatabase(session, cls)
