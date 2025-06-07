from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.controllers.create_entity_controller import (
    create_entity,
)
from src.api.controllers.update_entity_controller import (
    update_entity,
)
from src.api.dao.offer_dao import OfferDAO
from src.api.di.database import get_db
from src.schemas.offer_schema import OfferPostSchema, OfferPutSchema, OfferSchema

router = APIRouter(tags=["Offers"], prefix="/offers")


@router.get(
    "",
    response_model=Page[OfferSchema],
    summary="Return all offers with pagination or filter them",
    status_code=status.HTTP_200_OK,
)
# @cache(expire=60, coder=ORJsonCoder)
async def get_offers(
    db_session: AsyncSession = Depends(get_db),
    product_id: UUID | None = None,
    is_deleted: bool = False,
):
    filters = {"is_deleted": is_deleted}

    if product_id:
        filters["product_id"] = product_id

    return await OfferDAO.find_all_paginate(db_session, filter_by=filters)


@router.get(
    "/{offer_id}",
    response_model=OfferSchema,
    summary="Return offer by id",
    status_code=status.HTTP_200_OK,
)
async def get_offer(
    offer_id: UUID,
    db_session: AsyncSession = Depends(get_db),
):
    return await OfferDAO.find_by_id(db_session, offer_id)


@router.get(
    "/search",
    response_model=Page[OfferSchema],
    summary="Search offers by product name, cross_number, brand and manufacturer_number",
    status_code=status.HTTP_200_OK,
)
async def search_offers(
    search_term: str,
    db_session: AsyncSession = Depends(get_db),
):
    return await OfferDAO.smart_offer_search(db_session, search_term)


@router.get(
    "/text_search",
    response_model=Page[OfferSchema],
    summary="Search offers by product name, cross_number, brand and manufacturer_number",
    status_code=status.HTTP_200_OK,
)
async def full_text_search_offers(
    search_term: str,
    db_session: AsyncSession = Depends(get_db),
):
    return await OfferDAO.full_text_search(db_session, search_term)


@router.post(
    "",
    response_model=OfferSchema,
    summary="Create new offer",
    status_code=status.HTTP_201_CREATED,
)
async def post_offer(
    offer: OfferPostSchema,
    db_session: AsyncSession = Depends(get_db),
):
    return await create_entity(
        payload=offer,
        db_session=db_session,
        dao=OfferDAO,
        refresh_fields=["product"],
    )


@router.put(
    "/{offer_id}",
    response_model=OfferSchema,
    summary="Update offer by id",
    status_code=status.HTTP_200_OK,
)
async def put_offer(
    offer_id: UUID,
    offer: OfferPutSchema,
    db_session: AsyncSession = Depends(get_db),
):
    return await update_entity(
        entity_id=offer_id, payload=offer, dao=OfferDAO, db_session=db_session
    )


@router.delete(
    "/{offer_id}",
    summary="Delete offer by id",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_offer(
    offer_id: UUID,
    db_session: AsyncSession = Depends(get_db),
):
    success = await OfferDAO.delete_by_id(db_session, offer_id)
    if not success:
        raise HTTPException(status_code=404, detail="Offer not found")
