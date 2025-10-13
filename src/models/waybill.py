from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, uuid_pk
from src.schemas.common.enums import WaybillType

if TYPE_CHECKING:
    from src.models import Offer, Order, User, UserBalanceHistory, WaybillOffer


class Waybill(Base):
    id: Mapped[uuid_pk]
    author_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    customer_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    order_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("orders.id"), nullable=True, unique=True, index=True
    )

    waybill_type: Mapped[WaybillType] = mapped_column(
        SQLEnum(WaybillType, native_enum=False),
        nullable=False,
    )
    is_pending: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    note: Mapped[str] = mapped_column(String, nullable=True)

    # Relationships
    author: Mapped["User"] = relationship(
        "User",
        foreign_keys=[author_id],
        back_populates="created_waybills",
        lazy="joined",
    )
    customer: Mapped["User"] = relationship(
        "User",
        foreign_keys=[customer_id],
        back_populates="received_waybills",
        lazy="joined",
    )
    order: Mapped["Order"] = relationship(
        "Order",
        foreign_keys=[order_id],
        back_populates="waybill",
        lazy="noload",
        uselist=True,
    )
    waybill_offers: Mapped[list["WaybillOffer"]] = relationship(
        "WaybillOffer", back_populates="waybill", lazy="selectin"
    )
    user_balance_history: Mapped[list["UserBalanceHistory"]] = relationship(
        "UserBalanceHistory", back_populates="waybill", lazy="noload"
    )

    @property
    def offers(self) -> list["Offer"]:
        return [wo.offer for wo in self.waybill_offers]
