from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio import AsyncSession

from api.routes.fastapi_users_router import (
    current_active_user,
    require_employee,
)
from schemas.enums import WaybillType
from src.api.controllers.create_entity_controller import create_entity
from src.api.dao.offer_dao import OfferDAO
from src.api.dao.waybill_dao import WaybillDAO
from src.api.di.database import get_db
from src.api.services.waybill_service import WaybillService
from src.models.models import Product, Waybill
from src.schemas.waybill_offer_schema import WaybillOfferPostSchema, WaybillOfferSchema
from src.schemas.waybill_schema import WaybillPostSchema, WaybillSchema

router = APIRouter(
    tags=["Waybills"], prefix="/waybills", dependencies=[Depends(require_employee)]
)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=Page[WaybillSchema],
)
async def get_waybills(
    db_session: AsyncSession = Depends(get_db),
    waybill_type: WaybillType | None = None,
    is_pending: bool | None = None,
    user_id: UUID | None = None,
    search_term: str = "",
):
    """
    Get waybills by type and user ID
    """
    filters = {}
    if user_id:
        filters["user_id"] = user_id
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
)
async def get_waybill(
    waybill_id: UUID, db_session: AsyncSession = Depends(get_db)
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
)
async def count_offers(
    waybill_type: WaybillType | None = None,
    is_pending: bool | None = None,
    db_session: AsyncSession = Depends(get_db),
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
)
async def get_waybill_offers(
    waybill_id: UUID, db_session: AsyncSession = Depends(get_db)
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
)
async def create_waybill(
    waybill: WaybillPostSchema, db_session: AsyncSession = Depends(get_db)
):
    return await create_entity(
        payload=waybill,
        db_session=db_session,
        dao=WaybillDAO,
        refresh_fields=["user"],
    )


@router.post(
    "/{waybill_id}/commit",
    status_code=status.HTTP_201_CREATED,
    response_model=WaybillSchema,
)
async def commit_waybill(
    waybill_id: UUID,
    db_session: AsyncSession = Depends(get_db),
    user=Depends(current_active_user),
):
    return await WaybillService.commit(db_session, waybill_id, user.id)


@router.post(
    "/{waybill_id}/offers",
    status_code=status.HTTP_201_CREATED,
    response_model=WaybillOfferSchema,
)
async def add_offer_to_waybill(
    waybill_id: UUID,
    waybill_offer: WaybillOfferPostSchema,
    db_session: AsyncSession = Depends(get_db),
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
        address_id=offer.address_id,
        offer_id=offer.id,
        quantity=waybill_offer_obj.quantity,
        brand=waybill_offer_obj.brand,
        manufacturer_number=waybill_offer_obj.manufacturer_number,
        price_rub=waybill_offer_obj.price_rub,
        product_name=product.name,
        image_url=product.image_url,
        category_slug=product.sub_category.category_slug,
        sub_category_slug=product.sub_category_slug,
        category_name=product.sub_category.category_name,
        sub_category_name=product.sub_category.name,
        product_id=product.id,
    )


@router.delete(
    "/{waybill_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_waybill(waybill_id: UUID, db_session: AsyncSession = Depends(get_db)):
    deleted = await WaybillDAO.delete_by_id(db_session, waybill_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Waybill not found"
        )
    return
