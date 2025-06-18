import uuid
from datetime import datetime
from typing import Annotated, Any

from asyncpg import UniqueViolationError
from fastapi import HTTPException, status
from sqlalchemy import MetaData, func
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column

from src.config import settings
from src.utils.case_converter import camel_case_to_snake_case

# Annotations
uuid_pk = Annotated[
    uuid.UUID, mapped_column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
]
str_uniq = Annotated[str, mapped_column(unique=True, nullable=False)]
created_at = Annotated[
    datetime,
    mapped_column(TIMESTAMP(timezone=True), nullable=True, server_default=func.now()),
]
updated_at = Annotated[
    datetime,
    mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        server_default=func.now(),
        onupdate=func.now(),
    ),
]


class Base(DeclarativeBase):
    id: Any
    __name__: str

    metadata = MetaData(naming_convention=settings.DB.naming_convention)

    @declared_attr
    def __tablename__(self) -> str:
        """
        Generate __tablename__ automatically
        :return:
        """
        return f"{camel_case_to_snake_case(self.__name__)}s"

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    async def save(self, db_session: AsyncSession):
        """

        :param db_session:
        :return:
        """
        try:
            db_session.add(self)
            return await db_session.commit()
        except SQLAlchemyError as ex:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=repr(ex)
            ) from ex

    async def delete(self, db_session: AsyncSession):
        """

        :param db_session:
        :return:
        """
        try:
            await db_session.delete(self)
            await db_session.commit()
            return True
        except SQLAlchemyError as ex:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=repr(ex)
            ) from ex

    async def update(self, db: AsyncSession, **kwargs):
        """

        :param db:
        :param kwargs
        :return:
        """
        try:
            for k, v in kwargs.items():
                setattr(self, k, v)
            return await db.commit()
        except SQLAlchemyError as ex:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=repr(ex)
            ) from ex

    async def save_or_update(self, db: AsyncSession):
        try:
            db.add(self)
            return await db.commit()
        except IntegrityError as exception:
            if isinstance(exception.orig, UniqueViolationError):
                return await db.merge(self)
            else:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=repr(exception),
                ) from exception
        finally:
            await db.close()
