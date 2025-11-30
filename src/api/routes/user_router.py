from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.params import Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth.clerk import clerkClient, require_role
from src.api.core.update_entity import update_entity
from src.api.dao.user_dao import UserDAO
from src.api.di.db_helper import db_helper
from src.schemas.common.enums import CustomerType, Role
from src.schemas.user_schema import UserSchema, UserUpdate
from src.utils.logging import logger
from src.utils.pagination import Page

# Create the router
router = APIRouter(
    tags=["Users"],
    prefix="/users",
)


@router.get(
    "",
    response_model=Page[UserSchema],
    status_code=status.HTTP_200_OK,
    summary="Return all users with optional filters",
    dependencies=[Depends(require_role(Role.EMPLOYEE))],
)
async def get_users(
    db_session: AsyncSession = Depends(db_helper.session_getter),
    customer_type: CustomerType = None,
    search_term: str = Query("", description="name, phone or email"),
    role: Role | None = None,
):
    filters = {}

    if role:
        filters["role"] = role

    if customer_type:
        filters["customer_type"] = customer_type

    return await UserDAO.find_all_paginate(db_session, filters, search_term=search_term)


@router.get(
    "/{user_id}",
    response_model=UserSchema,
    status_code=status.HTTP_200_OK,
    summary="Return a single user by id",
    dependencies=[Depends(require_role(Role.USER))],
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
    dependencies=[Depends(require_role(Role.USER))],
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
    "/meta/count",
    response_model=dict[str, int],
    status_code=status.HTTP_200_OK,
    summary="Return count of users",
    dependencies=[Depends(require_role(Role.EMPLOYEE))],
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
    dependencies=[Depends(require_role(Role.EMPLOYEE))],
)
async def patch_user(
    user_id: UUID,
    payload: UserUpdate,
    db_session: AsyncSession = Depends(db_helper.session_getter),
):
    internal_user = await update_entity(
        entity_id=user_id, payload=payload, dao=UserDAO, db_session=db_session
    )
    await clerkClient.users.update_metadata_async(
        user_id=payload.clerk_id,
        public_metadata={
            "_id": internal_user.id,
            "_role": internal_user.role,
            "_customer_type": internal_user.customer_type,
        },
    )
    logger.info("[ClerkWebhook | PATCH] User metadata updated in Clerk")
    return internal_user
