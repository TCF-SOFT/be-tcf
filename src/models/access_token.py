from typing import TYPE_CHECKING
from fastapi_users_db_sqlalchemy import GUID
from fastapi_users_db_sqlalchemy.access_token import (
    SQLAlchemyBaseAccessTokenTableUUID,
    SQLAlchemyAccessTokenDatabase,
)
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, declared_attr
from src.models.base import Base

if TYPE_CHECKING:
    # Do not import, just use type with `session: "AsyncSession"`
    from sqlalchemy.ext.asyncio import AsyncSession


class AccessToken(Base, SQLAlchemyBaseAccessTokenTableUUID):
    """
    Table for storing access tokens.
    DB Strategy + Bearer Transport
    Due to table name `users` instead of `user`, the `user_id` is redefined
    """

    __tablename__ = "access_tokens"

    @declared_attr
    def user_id(cls) -> Mapped[GUID]:
        return mapped_column(
            GUID, ForeignKey("users.id", ondelete="cascade"), nullable=False
        )

    @classmethod
    def get_db(cls, session: "AsyncSession"):
        """
        Database Adapter
        """
        return SQLAlchemyAccessTokenDatabase(session, cls)
