from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base
from src.models.base import uuid_pk
from src.schemas.common.enums import CartStatus  # e.g. DRAFT, ORDERED

if TYPE_CHECKING:
    from src.models.cart_offer import CartOffer
    from src.models.user import User


class Cart(Base):
    __tablename__ = "carts"

    id: Mapped[uuid_pk]
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    status: Mapped[CartStatus] = mapped_column(
        SQLEnum(CartStatus, native_enum=False), default=CartStatus.DRAFT
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="carts", lazy="joined")
    cart_offers: Mapped[list["CartOffer"]] = relationship(
        "CartOffer",
        back_populates="cart",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
