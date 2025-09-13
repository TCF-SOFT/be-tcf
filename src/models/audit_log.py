from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    ForeignKey,
    String,
)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import uuid_pk, Base

if TYPE_CHECKING:
    from src.models import User


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[uuid_pk]
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    method: Mapped[str] = mapped_column(String, nullable=True)
    endpoint: Mapped[str] = mapped_column(String, nullable=True)
    payload: Mapped[dict] = mapped_column(JSON, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship(
        "User", back_populates="audit_log", lazy="joined"
    )
