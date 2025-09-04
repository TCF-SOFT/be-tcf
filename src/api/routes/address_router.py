from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.create_entity import create_entity
from api.core.update_entity import update_entity
from src.api.dao.address_dao import AddressDAO
from src.api.di.db_helper import db_helper
from src.schemas.address_schema import (
    AddressPatchSchema,
    AddressPostSchema,
    AddressSchema,
)

router = APIRouter(tags=["Address"], prefix="/addresses")


@router.get(
    "",
    response_model=list[AddressSchema],
    summary="Return all addresses",
    status_code=status.HTTP_200_OK,
)
async def get_addresses(
    user_id: UUID | None = None,
    db_session: AsyncSession = Depends(db_helper.session_getter),
):
    filters = {}
    if user_id:
        filters["user_id"] = user_id
    return await AddressDAO.find_all(db_session, filter_by=filters)


@router.get(
    "/{address_id}",
    response_model=AddressSchema,
    summary="Return address by id",
    status_code=status.HTTP_200_OK,
)
async def get_address(
    address_id: UUID, db_session: AsyncSession = Depends(db_helper.session_getter)
):
    res = await AddressDAO.find_by_id(db_session, address_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Address with id {address_id} not found.",
        )
    return res


@router.post(
    "",
    response_model=AddressSchema,
    summary="Create a new address",
    status_code=status.HTTP_201_CREATED,
)
async def post_address(
    payload: AddressPostSchema,
    db_session: AsyncSession = Depends(db_helper.session_getter),
):
    return await create_entity(payload=payload, db_session=db_session, dao=AddressDAO)


@router.patch(
    "/{address_id}",
    response_model=AddressSchema,
    summary="Update address by id",
    status_code=status.HTTP_200_OK,
    # dependencies=[Depends(require_clerk_session)],
)
async def patch_address(
    address_id: UUID,
    payload: AddressPatchSchema,
    db_session: AsyncSession = Depends(db_helper.session_getter),
):
    return await update_entity(
        entity_id=address_id, payload=payload, dao=AddressDAO, db_session=db_session
    )


@router.delete(
    "/{address_id}",
    summary="Delete address by id",
    status_code=status.HTTP_204_NO_CONTENT,
    # dependencies=[Depends(require_clerk_session)],
)
async def delete_address(
    address_id: UUID,
    db_session: AsyncSession = Depends(db_helper.session_getter),
):
    success = await AddressDAO.delete_by_id(db_session, address_id)
    if not success:
        raise HTTPException(status_code=404, detail="Address not found")
