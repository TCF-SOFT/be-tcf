import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, uuid_pk
from src.schemas.common.enums import WaybillType

if TYPE_CHECKING:
    from src.models.offer import Offer
    from src.models.user import User
    from src.models.waybill_offer import WaybillOffer


class Waybill(Base):
    id: Mapped[uuid_pk]
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    waybill_type: Mapped[WaybillType] = mapped_column(
        SQLEnum(WaybillType, native_enum=False),
        nullable=False,
    )
    is_pending: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    counterparty_name: Mapped[str] = mapped_column(String, nullable=False)
    note: Mapped[str] = mapped_column(String, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship(
        "User", back_populates="waybills", lazy="joined"
    )
    waybill_offers: Mapped[list["WaybillOffer"]] = relationship(
        "WaybillOffer", back_populates="waybill", lazy="selectin"
    )

    @property
    def offers(self) -> list["Offer"]:
        return [wo.offer for wo in self.waybill_offers]
