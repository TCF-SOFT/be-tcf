from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, uuid_pk

if TYPE_CHECKING:
    from src.models.offer import Offer
    from src.models.waybill import Waybill


class WaybillOffer(Base):
    """
    Визуальное отображение того, что пользователь выбрал на момент оформления.
     Это как бумажная накладная — она не меняется даже если продукт позже удалён или переименован.
    """

    id: Mapped[uuid_pk]
    waybill_id: Mapped[UUID] = mapped_column(ForeignKey("waybills.id"), nullable=False)
    offer_id: Mapped[UUID] = mapped_column(ForeignKey("offers.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    # Snapshot fields
    brand: Mapped[str] = mapped_column(String, nullable=False)
    manufacturer_number: Mapped[str] = mapped_column(String, nullable=True)
    price_rub: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False)

    # Relationships
    waybill: Mapped["Waybill"] = relationship(
        "Waybill", back_populates="waybill_offers", lazy="joined"
    )
    offer: Mapped["Offer"] = relationship(
        "Offer", back_populates="waybill_offers", lazy="joined"
    )
