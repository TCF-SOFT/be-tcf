from typing import TYPE_CHECKING

from sqlalchemy import (
    ForeignKey,
    Integer,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base
from src.models.base import uuid_pk

if TYPE_CHECKING:
    from src.models.offer import Offer
    from src.models.user import User


class CartOffer(Base):
    __tablename__ = "cart_offers"

    id: Mapped[uuid_pk]
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    offer_id: Mapped[str] = mapped_column(ForeignKey("offers.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(
        "User", back_populates="cart_offers", lazy="joined"
    )
    offer: Mapped["Offer"] = relationship(
        "Offer", back_populates="cart_offers", lazy="joined"
    )
