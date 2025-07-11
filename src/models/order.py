from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    ForeignKey,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base
from src.models.base import uuid_pk
from src.schemas.common.enums import OrderStatus

if TYPE_CHECKING:
    from src.models.address import Address
    from src.models.order_offer import OrderOffer
    from src.models.user import User


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[uuid_pk]
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    address_id: Mapped[UUID] = mapped_column(ForeignKey("addresses.id"), nullable=False)
    status: Mapped[OrderStatus]
    note: Mapped[str] = mapped_column(String, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="orders", lazy="joined")
    address: Mapped["Address"] = relationship(
        "Address", back_populates="orders", lazy="joined"
    )
    order_offers: Mapped[list["OrderOffer"]] = relationship(
        "OrderOffer", back_populates="order", lazy="selectin"
    )

    @property
    def total_sum(self) -> float:
        return sum([offer.price_rub for offer in self.order_offers])
