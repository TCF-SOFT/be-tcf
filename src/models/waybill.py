import uuid

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from schemas.common.enums import WaybillType
from src.models.base import Base, uuid_pk


class Waybill(Base):
    id: Mapped[uuid_pk]
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    waybill_type: Mapped[WaybillType] = mapped_column(
        SQLEnum(WaybillType, native_enum=False),
        nullable=False,
    )
    is_pending: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    counterparty_name: Mapped[str] = mapped_column(String, nullable=False)

    # Relationships
    user = relationship("User", back_populates="waybills", lazy="joined")
    waybill_offers = relationship(
        "WaybillOffer", back_populates="waybill", lazy="joined"
    )

    @property
    def author(self) -> str:
        """
        Proxy `user.name` so Pydantic can see it.
        """
        return self.user.first_name
