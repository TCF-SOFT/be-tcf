from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dao.user_dao import UserDAO
from src.api.di.db_helper import db_helper
from src.api.routes.fastapi_users_router import fastapi_users_router, require_employee
from src.schemas.common.enums import Role
from src.schemas.user_schema import UserRead, UserUpdate

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
    db_session: AsyncSession = Depends(db_helper.session_getter),
    role: Role | None = None,
):
    filters = {}

    if role:
        filters["role"] = role

    return await UserDAO.find_all(db_session, filters)


@router.get(
    "/meta/count",
    response_model=dict[str, int],
    status_code=status.HTTP_200_OK,
    summary="Return count of users",
    dependencies=[Depends(require_employee)],
)
async def count_users(
    db_session: AsyncSession = Depends(db_helper.session_getter),
    role: Role | None = None,
):
    filters = {}

    if role:
        filters["role"] = role

    return await UserDAO.count_all(db_session, filters)
