from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, uuid_pk
from src.schemas.common.enums import WaybillType

if TYPE_CHECKING:
    from src.models.offer import Offer
    from src.models.user import User
    from src.models.waybill import Waybill


class StockMovement(Base):
    id: Mapped[uuid_pk]

    offer_id: Mapped[UUID] = mapped_column(ForeignKey("offers.id"), nullable=False)
    waybill_id: Mapped[UUID] = mapped_column(ForeignKey("waybills.id"), nullable=True)

    waybill_type: Mapped[WaybillType] = mapped_column(
        SQLEnum(WaybillType, native_enum=False),
        nullable=False,
    )

    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    comment: Mapped[str | None] = mapped_column(String, nullable=True)

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    reverted: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    offer: Mapped["Offer"] = relationship("Offer", lazy="joined")
    user: Mapped["User"] = relationship("User", lazy="joined")
    waybill: Mapped["Waybill"] = relationship("Waybill", lazy="joined")
