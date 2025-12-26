from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base
from src.models.base import uuid_pk

if TYPE_CHECKING:
    from src.models.order_offer import OrderOffer
    from src.models.user import User
    from src.models.waybill import Waybill


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[uuid_pk]
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)

    status: Mapped[str]
    note: Mapped[str | None]

    country: Mapped[str | None]
    city: Mapped[str | None]
    street: Mapped[str | None]
    house: Mapped[str | None]
    postal_code: Mapped[str | None]
    shipping_company: Mapped[str | None]
    shipping_method: Mapped[str]

    first_name: Mapped[str]
    last_name: Mapped[str]
    phone: Mapped[str]

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="orders", lazy="joined")
    waybill: Mapped["Waybill"] = relationship(
        "Waybill",
        back_populates="order",
        uselist=False,
        lazy="selectin",
    )
    order_offers: Mapped[list["OrderOffer"]] = relationship(
        "OrderOffer", back_populates="order", lazy="selectin"
    )

    @property
    def total_sum(self) -> float:
        return sum([offer.price_rub * offer.quantity for offer in self.order_offers])
