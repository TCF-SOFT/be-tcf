from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth.clerk import require_role
from src.api.core.update_entity import update_entity
from src.api.dao.offer_dao import OfferDAO
from src.api.dao.waybill_dao import WaybillDAO
from src.api.di.db_helper import db_helper
from src.api.services.waybill_service import WaybillService
from src.models import Product, Waybill
from src.schemas.common.enums import Role, WaybillType
from src.schemas.offer_schema import OfferSchema
from src.schemas.waybill_offer_schema import WaybillOfferPostSchema, WaybillOfferSchema
from src.schemas.waybill_schema import (
    WaybillPatchSchema,
    WaybillSchema,
    WaybillWithOffersInternalPostSchema,
    WaybillWithOffersPostSchema,
)

router = APIRouter(
    tags=["Waybills"],
    prefix="/waybills",
)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=Page[WaybillSchema],
    dependencies=[Depends(require_role(Role.EMPLOYEE))],
)
async def get_waybills(
    db_session: AsyncSession = Depends(db_helper.session_getter),
    waybill_type: WaybillType | None = None,
    is_pending: bool | None = None,
    search_term: str = "",
):
    """
    Get waybills with optional filters
    """
    filters = {}
    if waybill_type:
        filters["waybill_type"] = waybill_type
    if is_pending is not None:
        filters["is_pending"] = is_pending
    return await WaybillDAO.find_all_paginate(
        db_session, filter_by=filters, search_term=search_term
    )


@router.get(
    "/{waybill_id}",
    status_code=status.HTTP_200_OK,
    response_model=WaybillSchema,
    dependencies=[Depends(require_role(Role.USER))],
)
async def get_waybill(
    waybill_id: UUID, db_session: AsyncSession = Depends(db_helper.session_getter)
) -> WaybillSchema | None:
    """
    Get waybill by ID
    """
    res = await WaybillDAO.find_by_id(db_session, waybill_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Waybill not found"
        )
    return res


@router.get(
    "/meta/count",
    response_model=dict[str, int],
    summary="Return count of waybills",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_role(Role.EMPLOYEE))],
)
async def count_waybills(
    waybill_type: WaybillType | None = None,
    is_pending: bool | None = None,
    db_session: AsyncSession = Depends(db_helper.session_getter),
):
    filters = {}

    if waybill_type:
        filters["waybill_type"] = waybill_type
    if is_pending is not None:
        filters["is_pending"] = is_pending

    return await WaybillDAO.count_all(db_session, filter_by=filters)


@router.get(
    "/{waybill_id}/offers",
    status_code=status.HTTP_200_OK,
    response_model=list[WaybillOfferSchema],
    dependencies=[Depends(require_role(Role.EMPLOYEE))],
)
async def get_waybill_offers(
    waybill_id: UUID, db_session: AsyncSession = Depends(db_helper.session_getter)
):
    """
    Get all offers in waybill
    """
    waybill: Waybill = await WaybillDAO.find_by_id(db_session, waybill_id)
    if not waybill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Waybill not found"
        )

    return await WaybillService.fetch_waybill_offers(waybill)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=WaybillSchema,
    dependencies=[Depends(require_role(Role.EMPLOYEE))],
)
async def create_waybill(
    payload: WaybillWithOffersPostSchema,
    author_id: UUID = Depends(require_role(Role.EMPLOYEE)),
    db_session: AsyncSession = Depends(db_helper.session_getter_manual),
):
    internal = WaybillWithOffersInternalPostSchema(
        author_id=author_id, **payload.model_dump()
    )

    # If customer_id is not provided, set it to author_id
    if internal.customer_id is None:
        internal.customer_id = internal.author_id

    return await WaybillService.post_waybill_with_offers(db_session, internal)


@router.patch(
    "/{waybill_id}",
    status_code=status.HTTP_200_OK,
    response_model=WaybillSchema,
    dependencies=[Depends(require_role(Role.EMPLOYEE))],
)
async def patch_waybill(
    waybill_id: UUID,
    payload: WaybillPatchSchema,
    db_session: AsyncSession = Depends(db_helper.session_getter),
):
    return await update_entity(
        entity_id=waybill_id,
        payload=payload,
        dao=WaybillDAO,
        db_session=db_session,
    )


@router.post(
    "/{waybill_id}/commit",
    status_code=status.HTTP_201_CREATED,
    response_model=WaybillSchema,
)
async def commit_waybill(
    waybill_id: UUID,
    db_session: AsyncSession = Depends(db_helper.session_getter),
    user_id=Depends(require_role(Role.EMPLOYEE)),
):
    return await WaybillService.commit(db_session, waybill_id, user_id)


@router.post(
    "/{waybill_id}/offers",
    status_code=status.HTTP_201_CREATED,
    response_model=WaybillOfferSchema,
    dependencies=[Depends(require_role(Role.EMPLOYEE))],
)
async def add_offer_to_waybill(
    waybill_id: UUID,
    waybill_offer: WaybillOfferPostSchema,
    db_session: AsyncSession = Depends(db_helper.session_getter),
):
    # получаем текущие данные из offers — для валидации
    offer = await OfferDAO.find_by_id(db_session, waybill_offer.offer_id)
    if not offer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Offer not found"
        )

    product: Product = offer.product
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    waybill_offer_obj = await WaybillService.add_offer_to_waybill(
        db_session, waybill_id, waybill_offer
    )

    return WaybillOfferSchema(
        id=waybill_offer_obj.id,
        waybill_id=waybill_id,
        offer_id=offer.id,
        offer=OfferSchema.model_validate(offer),
        quantity=waybill_offer_obj.quantity,
        brand=waybill_offer_obj.brand,
        manufacturer_number=waybill_offer_obj.manufacturer_number,
        price_rub=waybill_offer_obj.price_rub,
    )


@router.delete(
    "/{waybill_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role(Role.EMPLOYEE))],
)
async def delete_waybill(
    waybill_id: UUID, db_session: AsyncSession = Depends(db_helper.session_getter)
):
    deleted = await WaybillDAO.delete_by_id(db_session, waybill_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Waybill not found"
        )
    return
