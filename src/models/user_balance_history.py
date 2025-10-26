from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    ForeignKey,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, uuid_pk
from src.schemas.common.enums import Currency, UserBalanceChangeReason

if TYPE_CHECKING:
    from src.models import User, Waybill


class UserBalanceHistory(Base):
    __tablename__ = "user_balance_history"

    id: Mapped[uuid_pk]
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    waybill_id: Mapped[UUID] = mapped_column(ForeignKey("waybills.id"), nullable=True)

    delta: Mapped[int] = mapped_column(BigInteger, nullable=False)
    balance_before: Mapped[int] = mapped_column(BigInteger, nullable=False)
    balance_after: Mapped[int] = mapped_column(BigInteger, nullable=False)
    currency: Mapped[Currency] = mapped_column(String(3), nullable=False)
    reason: Mapped[UserBalanceChangeReason] = mapped_column(String, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(
        "User", back_populates="user_balance_history", lazy="joined"
    )
    waybill: Mapped["Waybill"] = relationship(
        "Waybill", back_populates="user_balance_history", lazy="joined"
    )
