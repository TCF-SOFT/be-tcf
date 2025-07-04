import uuid
from typing import TYPE_CHECKING, Optional

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
    from src.models.cart_offer import CartOffer
    from src.models.waybill_offer import WaybillOffer


class Offer(Base):
    id: Mapped[uuid_pk]
    # TODO: rename to SKU (pydantic + zod)
    address_id: Mapped[str] = mapped_column(String, nullable=True)
    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("products.id"), nullable=False
    )
    offer_bitrix_id: Mapped[str] = mapped_column(String, nullable=True)

    brand: Mapped[str] = mapped_column(String, nullable=False)
    manufacturer_number: Mapped[str] = mapped_column(String, nullable=True)
    internal_description: Mapped[str] = mapped_column(Text, nullable=True)

    price_rub: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False)
    super_wholesale_price_rub: Mapped[float] = mapped_column(
        Numeric(12, 4), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    # Soft delete field
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    product: Mapped["Product"] = relationship(
        "Product", back_populates="offers", lazy="joined"
    )
    waybill_offers: Mapped[list["WaybillOffer"]] = relationship(
        "WaybillOffer", back_populates="offer", lazy="joined"
    )
    order_offers: Mapped[list["OrderOffer"]] = relationship(
        "OrderOffer", back_populates="offer", lazy="joined"
    )
    cart_offers: Mapped[list["CartOffer"]] = relationship(
        "CartOffer", back_populates="offer", lazy="joined"
    )

    # <-- Pydantic tiny helpers ------------------------------
    @property
    def image_url(self) -> Optional[str]:
        """Proxy `product.image_url` so Pydantic can see it."""
        return self.product.image_url if self.product else None

    @property
    def sub_category_slug(self) -> str:
        return self.product.sub_category_slug

    @property
    def sub_category_name(self) -> str:
        """
        WaybillOffer and Offer use this to display sub-category name.
        """
        return self.product.sub_category.name

    @property
    def category_slug(self) -> str:
        return self.product.sub_category.category_slug

    @property
    def category_name(self) -> str:
        """
        WaybillOffer and Offer use this to display category name.
        """
        return self.product.sub_category.category.name

    @property
    def product_name(self) -> str:
        return self.product.name

    @property
    def cross_number(self) -> Optional[str]:
        """
        Proxy `product.cross_number` so Pydantic can see it.
        """
        return self.product.cross_number if self.product else None

    # --------------------------------------------------------
