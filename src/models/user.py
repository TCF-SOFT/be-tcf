from typing import Literal, Optional

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from sqlalchemy import (
    Boolean,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, str_uniq, uuid_pk


class User(Base, SQLAlchemyBaseUserTableUUID):
    __tablename__ = "users"

    id: Mapped[uuid_pk]
    email: Mapped[str_uniq]
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    role: Mapped[Literal["admin", "employee", "user"]] = mapped_column(
        String, nullable=False, default="user"
    )

    position: Mapped[Literal["Менеджер", "Кладовщик"]] = mapped_column(
        String, nullable=True
    )

    # Relationships
    waybills = relationship("Waybill", back_populates="user", lazy="joined")
