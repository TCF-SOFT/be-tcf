from typing import TYPE_CHECKING

from sqlalchemy import (
    UUID,
    ForeignKey,
    Integer,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base
from src.models.base import uuid_pk

if TYPE_CHECKING:
    from src.models.cart import Cart
    from src.models.offer import Offer


class CartOffer(Base):
    __tablename__ = "cart_offers"

    id: Mapped[uuid_pk]
    cart_id: Mapped[UUID] = mapped_column(ForeignKey("carts.id"), nullable=False)
    offer_id: Mapped[UUID] = mapped_column(ForeignKey("offers.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    offer: Mapped["Offer"] = relationship(
        "Offer", back_populates="cart_offers", lazy="joined"
    )
    cart: Mapped["Cart"] = relationship(
        "Cart", back_populates="cart_offers", lazy="joined"
    )
