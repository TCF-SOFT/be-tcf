from uuid import UUID

from clerk_backend_api import Clerk
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth.clerk import clerkClient, require_clerk_session
from src.api.controllers.update_entity_controller import update_entity
from src.api.dao.user_dao import UserDAO
from src.api.di.db_helper import db_helper
from src.schemas.common.enums import Role
from src.schemas.user_schema import UserSchema, UserUpdate
from utils.logging import logger

# Create the router
router = APIRouter(
    tags=["Users"],
    prefix="/users",
    dependencies=[Depends(require_clerk_session)],
)


@router.get(
    "",
    response_model=list[UserSchema],
    status_code=status.HTTP_200_OK,
    summary="Return all users or filter them",
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
    "/{user_id}",
    response_model=UserSchema,
    status_code=status.HTTP_200_OK,
    summary="Return a single user by id",
)
async def get_user_by_id(
    user_id: UUID,
    db_session: AsyncSession = Depends(db_helper.session_getter),
):
    return await UserDAO.find_by_id(db_session, user_id)


@router.get(
    "/clerk/{clerk_id}",
    response_model=UserSchema,
    status_code=status.HTTP_200_OK,
    summary="Return a single user by id",
)
async def get_user_by_clerk_id(
    clerk_id: str,
    db_session: AsyncSession = Depends(db_helper.session_getter),
):
    res = await UserDAO.find_by_clerk_id(db_session, clerk_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with clerk_id {clerk_id} not found.",
        )
    return res


@router.get(
    "/search/wildcard",
    response_model=Page[UserSchema],
    status_code=status.HTTP_200_OK,
    summary="Search users by wildcard",
)
async def search_users(
    search_term: str,
    db_session: AsyncSession = Depends(db_helper.session_getter),
):
    """
    Search users by wildcard.
    """
    return await UserDAO.wildcard_search(db_session, search_term)


@router.get(
    "/meta/count",
    response_model=dict[str, int],
    status_code=status.HTTP_200_OK,
    summary="Return count of users",
)
async def count_users(
    db_session: AsyncSession = Depends(db_helper.session_getter),
    role: Role | None = None,
):
    filters = {}

    if role:
        filters["role"] = role

    return await UserDAO.count_all(db_session, filters)


@router.patch(
    "/{user_id}",
    response_model=UserSchema,
    status_code=status.HTTP_200_OK,
    summary="Selective update a user by id",
)
async def patch_user(
    user_id: UUID,
    payload: UserUpdate,
    db_session: AsyncSession = Depends(db_helper.session_getter),
    clerk_client: Clerk = Depends(clerkClient),
):
    internal_user = await update_entity(
        entity_id=user_id, payload=payload, dao=UserDAO, db_session=db_session
    )
    await clerk_client.users.update_metadata_async(
        user_id=payload.clerk_id,
        public_metadata={
            "_id": internal_user.id,
            "_role": internal_user.role,
            "_customer_type": internal_user.customer_type,
        },
    )
    logger.info("[ClerkWebhook | PATCH] User metadata updated in Clerk")
    return internal_user
