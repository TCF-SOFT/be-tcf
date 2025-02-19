import uuid
from typing import Literal, Optional

import sqlalchemy.sql
from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, str_uniq, uuid_pk


class User(Base):
    id: Mapped[uuid_pk]
    email: Mapped[str_uniq]
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    role: Mapped[Literal["admin", "customer", "king"]] = mapped_column(
        String, nullable=False, default="user"
    )

    # Ассоциация с таблицей Order (1 user -> M orders)
    orders = relationship(
        "Order", back_populates="user", cascade="all, delete-orphan", lazy="selectin"
    )

    # Ассоциация с таблицей Cart (1 user -> 1 cart)
    cart = relationship(
        "Cart", back_populates="user", cascade="all, delete-orphan", lazy="selectin"
    )

    # Ассоциация с таблицей Rating (1 user -> M ratings)
    ratings = relationship(
        "Rating", back_populates="user", cascade="all, delete-orphan", lazy="selectin"
    )

    def __str__(self):
        return f"User: {self.email}"


class Order(Base):
    id: Mapped[uuid_pk]
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    user_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False, default="pending")

    # Associations
    user = relationship("User", back_populates="orders", lazy="selectin")
    order_cocktails = relationship(
        "Cocktail",
        secondary="order_cocktails",
        back_populates="cocktail_orders",
        lazy="selectin",
    )

    def __str__(self):
        return f"Order: {self.id}"


class OrderCocktail(Base):
    __tablename__ = "order_cocktails"
    order_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("orders.id"), primary_key=True
    )
    cocktail_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("cocktails.id"), primary_key=True
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class Cocktail(Base):
    id: Mapped[uuid_pk]
    name = Column(String(100), nullable=False)
    description = Column(Text)
    recipe = Column(Text)
    alcohol_content = Column(Float)
    in_stock: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=sqlalchemy.sql.true()
    )
    drink_type = Column(String(100))

    # Ассоциация с таблицей Image (1 cocktail -> M images)
    # Using 'selectin' loading to efficiently load images in a separate query immediately after the main query
    # check readme for more info
    images = relationship(
        "Image",
        back_populates="cocktail",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    # Ассоциация с таблицей Rating (1 cocktail -> M ratings)
    ratings = relationship(
        "Rating",
        back_populates="cocktail",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    # Ассоциация с таблицей Label через `cocktail_labels` (M cocktails -> M labels)
    labels = relationship(
        "Label",
        secondary="cocktail_labels",
        back_populates="cocktails",
        lazy="selectin",
    )
    # Ассоциация с таблицей Order через `order_cocktails` (M cocktails -> M orders)
    cocktail_orders = relationship(
        "Order",
        secondary="order_cocktails",
        back_populates="order_cocktails",
        lazy="select",
    )

    def __str__(self):
        return f"Cocktail: {self.name}"


class Image(Base):
    id: Mapped[uuid_pk]
    cocktail_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("cocktails.id"), nullable=False
    )
    image_url: Mapped[str] = mapped_column(String, nullable=True)
    is_thumbnail: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    cocktail = relationship("Cocktail", back_populates="images", lazy="select")

    def __str__(self):
        return f"Image: {self.image_url}"


class Label(Base):
    id: Mapped[uuid_pk]
    name = Column(String(100), nullable=False)

    cocktails = relationship(
        "Cocktail",
        secondary="cocktail_labels",
        back_populates="labels",
        lazy="select",
    )

    def __str__(self):
        return f"Label: {self.name}"


class CocktailLabel(Base):
    __tablename__ = "cocktail_labels"
    cocktail_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("cocktails.id"), primary_key=True
    )
    label_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("labels.id"), primary_key=True
    )


class Cart(Base):
    id: Mapped[uuid_pk]
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Ассоциация с таблицей User (1 cart -> 1 user)
    user = relationship("User", back_populates="cart", lazy="selectin")
    # Ассоциация с таблицей Cocktail через `cart_items` (M carts -> M cocktails)
    cart_items = relationship("CartItem", back_populates="cart", lazy="selectin")

    def to_dict(self):
        return {"id": self.id, "user_id": self.user, "cocktails": self.cart_items}


class CartItem(Base):
    __tablename__ = "cart_items"
    cart_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("carts.id"), primary_key=True)
    cocktail_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("cocktails.id"), primary_key=True
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Relationship with Cart (M cart_items -> 1 cart)
    cart = relationship("Cart", back_populates="cart_items")

    # Relationship with Cocktail (M cart_items -> 1 cocktail)
    cocktail = relationship("Cocktail", lazy="selectin")


class Rating(Base):
    id: Mapped[uuid_pk]
    cocktail_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("cocktails.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)

    # Relationship with User
    user = relationship("User", back_populates="ratings", lazy="selectin")

    # Relationship with Cocktail
    cocktail = relationship("Cocktail", back_populates="ratings", lazy="select")

    def __str__(self):
        return f"Rating: {self.rating}"
