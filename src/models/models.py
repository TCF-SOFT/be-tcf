import uuid
from typing import Literal, Optional

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, uuid_pk


class StockMovement(Base):
    id: Mapped[uuid_pk]

    offer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("offers.id"), nullable=False)
    waybill_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("waybills.id"), nullable=True
    )

    waybill_type: Mapped[Literal["WAYBILL_IN", "WAYBILL_OUT", "WAYBILL_RETURN"]] = (
        mapped_column(String, nullable=False)
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    comment: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    reverted: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    offer = relationship("Offer", lazy="joined")
    user = relationship("User", lazy="joined")
    waybill = relationship("Waybill", lazy="joined")


class WaybillOffer(Base):
    """
    Визуальное отображение того, что пользователь выбрал на момент оформления.
     Это как бумажная накладная — она не меняется даже если продукт позже удалён или переименован.
    """

    id: Mapped[uuid_pk]
    waybill_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("waybills.id"), nullable=False
    )
    offer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("offers.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    # Snapshot fields
    brand: Mapped[str] = mapped_column(String, nullable=False)
    manufacturer_number: Mapped[str] = mapped_column(String, nullable=True)
    price_rub: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False)

    # Relationships
    waybill = relationship("Waybill", back_populates="waybill_offers", lazy="joined")
    offer = relationship("Offer", back_populates="waybill_offers", lazy="joined")
