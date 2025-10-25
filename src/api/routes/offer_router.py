from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth.clerk import require_role
from src.api.core.create_entity import (
    create_entity_with_optional_image,
)
from common.deps.s3_service import get_s3_service
from common.services.s3_service import S3Service
from src.schemas.common.enums import Role
from src.api.core.update_entity import (
    update_entity_with_optional_image,
)
from src.api.dao.offer_dao import OfferDAO
from src.api.di.db_helper import db_helper
from src.schemas.offer_schema import OfferPatchSchema, OfferPostSchema, OfferSchema

router = APIRouter(tags=["Offers"], prefix="/offers")


@router.get(
    "",
    response_model=Page[OfferSchema],
    summary="Return all offers with pagination or filter them",
    status_code=status.HTTP_200_OK,
)
# @cache(expire=60, coder=ORJsonCoder)
async def get_offers(
    db_session: AsyncSession = Depends(db_helper.session_getter),
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
    db_session: AsyncSession = Depends(db_helper.session_getter),
):
    return await OfferDAO.find_by_id(db_session, offer_id)


@router.get(
    "/meta/count",
    response_model=dict[str, int],
    summary="Return count of offers",
    status_code=status.HTTP_200_OK,
)
async def count_offers(
    # TODO: add counts by categories
    # category_slug: str | None = None,
    # sub_category_slug: str | None = None,
    product_id: UUID | None = None,
    in_stock: bool | None = None,
    is_image: bool | None = None,
    db_session: AsyncSession = Depends(db_helper.session_getter),
):
    filters = {}

    if product_id:
        filters["product_id"] = product_id
    if in_stock:
        filters["in_stock"] = in_stock
    if is_image is not None:
        filters["is_image"] = is_image

    return await OfferDAO.count_all(db_session, filter_by=filters)


@router.get(
    "/search/wildcard",
    response_model=Page[OfferSchema],
    summary="Search offers by product name, cross_number, brand and manufacturer_number",
    status_code=status.HTTP_200_OK,
)
async def search_offers(
    search_term: str,
    db_session: AsyncSession = Depends(db_helper.session_getter),
):
    return await OfferDAO.smart_offer_search(db_session, search_term)


@router.get(
    "/search/text_search",
    response_model=Page[OfferSchema],
    summary="Search offers by product name, cross_number, brand and manufacturer_number",
    status_code=status.HTTP_200_OK,
)
async def full_text_search_offers(
    search_term: str,
    db_session: AsyncSession = Depends(db_helper.session_getter),
):
    return await OfferDAO.full_text_search(db_session, search_term)


@router.post(
    "",
    response_model=OfferSchema,
    summary="Create new offer",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(Role.EMPLOYEE))],
)
async def post_offer(
    payload: Annotated[OfferPostSchema, Depends(OfferPostSchema.as_form)],
    image_blob: UploadFile | None = File(None),
    db_session: AsyncSession = Depends(db_helper.session_getter),
    s3: S3Service = Depends(get_s3_service),
):
    return await create_entity_with_optional_image(
        payload=payload,
        image_blob=image_blob,
        upload_path="images/tmp",
        db_session=db_session,
        s3=s3,
        dao=OfferDAO,
        refresh_fields=["product"],
    )


@router.patch(
    "/{offer_id}",
    response_model=OfferSchema,
    summary="Update offer by id",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_role(Role.EMPLOYEE))],
)
async def patch_offer(
    offer_id: UUID,
    payload: Annotated[OfferPatchSchema, Depends(OfferPatchSchema.as_form)],
    image_blob: UploadFile | None = File(None),
    db_session: AsyncSession = Depends(db_helper.session_getter),
    s3: S3Service = Depends(get_s3_service),
):
    return await update_entity_with_optional_image(
        entity_id=offer_id,
        payload=payload,
        dao=OfferDAO,
        upload_path="images/tmp",
        db_session=db_session,
        s3=s3,
        image_blob=image_blob,
    )


@router.delete(
    "/{offer_id}",
    summary="Delete offer by id",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
async def delete_offer(
    offer_id: UUID,
    db_session: AsyncSession = Depends(db_helper.session_getter),
):
    success = await OfferDAO.delete_by_id(db_session, offer_id)
    if not success:
        raise HTTPException(status_code=404, detail="Offer not found")
