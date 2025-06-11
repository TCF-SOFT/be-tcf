from typing import Literal

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.routes.fastapi_users_router import fastapi_users_router, require_employee
from schemas.user_schema import UserUpdate
from src.api.dao.user_dao import UserDAO
from src.api.di.database import get_db
from src.schemas.user_schema import UserRead

# Create the router
router = APIRouter(tags=["Users"], prefix="/users")

# /me
# /{id}
router.include_router(
    router=fastapi_users_router.get_users_router(UserRead, UserUpdate)
)


@router.get(
    "",
    response_model=list[UserRead],
    status_code=status.HTTP_200_OK,
    summary="Return all users or filter them",
    dependencies=[Depends(require_employee)],
)
async def get_users(
    db_session: AsyncSession = Depends(get_db),
    role: Literal["admin", "employee", "user"] | None = None,
):
    filters = {}

    if role:
        filters["role"] = role

    return await UserDAO.find_all(db_session, filters)
