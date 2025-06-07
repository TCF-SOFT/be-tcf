from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dao.user_dao import UserDAO
from src.api.di.database import get_db
from src.schemas.user_schema import UserRead

# Create the router
router = APIRouter(tags=["Users"])


@router.get(
    "/users",
    response_model=list[UserRead],
    summary="Return all users or filter them",
)
async def get_users(
    db_session: AsyncSession = Depends(get_db),
    role: Literal["admin", "employee", "user"] | None = None,
):
    filters = {}

    if role:
        filters["role"] = role

    return await UserDAO.find_all(db_session, filters)


@router.get(
    "/users/{user_id}",
    response_model=UserRead,
    summary="Return user by id",
)
async def get_user(
    user_id: UUID,
    db_session: AsyncSession = Depends(get_db),
):
    return await UserDAO.find_by_id(db_session, user_id)


