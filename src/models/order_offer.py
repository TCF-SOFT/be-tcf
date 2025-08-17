from typing import TYPE_CHECKING

from sqlalchemy import (
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base
from src.models.base import uuid_pk

if TYPE_CHECKING:
    from src.models.offer import Offer
    from src.models.order import Order


class OrderOffer(Base):
    __tablename__ = "order_offers"

    id: Mapped[uuid_pk]
    order_id: Mapped[uuid_pk] = mapped_column(ForeignKey("orders.id"), nullable=False)
    offer_id: Mapped[uuid_pk] = mapped_column(ForeignKey("offers.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    # Snapshot fields
    brand: Mapped[str] = mapped_column(String, nullable=False)
    manufacturer_number: Mapped[str] = mapped_column(String, nullable=True)
    price_rub: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False)

    # Relationships
    order: Mapped["Order"] = relationship(
        "Order", back_populates="order_offers", lazy="select"
    )
    offer: Mapped["Offer"] = relationship(
        "Offer", back_populates="order_offers", lazy="joined"
    )
