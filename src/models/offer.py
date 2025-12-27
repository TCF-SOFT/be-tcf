from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, uuid_pk
from src.models.order_offer import OrderOffer

if TYPE_CHECKING:
    from src.models import Product
    from src.models.waybill_offer import WaybillOffer


class Offer(Base):
    id: Mapped[uuid_pk]
    sku: Mapped[str] = mapped_column(String, nullable=True)
    product_id: Mapped[UUID] = mapped_column(ForeignKey("products.id"), nullable=False)
    offer_bitrix_id: Mapped[str] = mapped_column(String, nullable=True)

    brand: Mapped[str] = mapped_column(String, nullable=False)
    manufacturer_number: Mapped[str] = mapped_column(String, nullable=False)
    internal_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str] = mapped_column(String, nullable=True)

    price_rub: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False)
    super_wholesale_price_rub: Mapped[float] = mapped_column(
        Numeric(12, 4), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Soft delete field
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    product: Mapped["Product"] = relationship(
        "Product", back_populates="offers", lazy="joined"
    )
    waybill_offers: Mapped[list["WaybillOffer"]] = relationship(
        "WaybillOffer", back_populates="offer", lazy="select"
    )
    order_offers: Mapped[list["OrderOffer"]] = relationship(
        "OrderOffer", back_populates="offer", lazy="select"
    )
