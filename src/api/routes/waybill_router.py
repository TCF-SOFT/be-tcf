import uuid
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.controllers.create_entity_controller import create_entity
from src.api.dao.offer_dao import OfferDAO
from src.api.dao.waybill_offer_dao import WaybillOfferDAO
from src.models.models import Product, Offer
from src.api.dao.waybill_dao import WaybillDAO
from src.api.di.database import get_db
from src.api.services.waybill_service import WaybillService
from src.models.models import Waybill
from src.schemas.waybill_offer_schema import WaybillOfferPostSchema, WaybillOfferSchema
from src.schemas.waybill_schema import WaybillPostSchema, WaybillSchema
from src.tasks.tasks import send_waybill_confirmation_email

router = APIRouter(tags=["Waybill"])


@router.get("/waybill/{email}", status_code=200)
async def send_waybill(email: EmailStr) -> None:
    """
    Send waybill to email
    """
    # for i in range(5):
    send_waybill_confirmation_email.delay(email=email)


@router.get("/waybills", status_code=200, response_model=Page[WaybillSchema])
async def get_waybills(
    db_session: AsyncSession = Depends(get_db),
    waybill_type: Literal["WAYBILL_IN", "WAYBILL_OUT", "WAYBILL_RETURN"] | None = None,
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


@router.get("/waybills/{waybill_id}", status_code=200, response_model=WaybillSchema)
async def get_waybill(
    waybill_id: UUID, db_session: AsyncSession = Depends(get_db)
) -> WaybillSchema | None:
    """
    Get waybill by ID
    """
    return await WaybillDAO.find_by_id(db_session, waybill_id)


@router.get(
    "/waybills/{waybill_id}/offers",
    status_code=200,
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
        raise HTTPException(status_code=404, detail="Waybill not found")

    return await WaybillService.fetch_waybill_offers(waybill)


def get_current_user():
    return uuid.UUID("b5fe5a3b-dfa2-43d3-a81e-34404d8f75d4")


@router.post("/waybill", status_code=201, response_model=WaybillSchema)
async def create_waybill(
    waybill: WaybillPostSchema,
    db_session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    return await create_entity(
        payload=waybill,
        db_session=db_session,
        dao=WaybillDAO,
        refresh_fields=["user"],
    )


@router.post(
    "/waybill/{waybill_id}/commit", status_code=201, response_model=WaybillSchema
)
async def commit_waybill(
    waybill_id: UUID,
    db_session: AsyncSession = Depends(get_db),
    user_id=Depends(get_current_user),
):
    return await WaybillService.commit(db_session, waybill_id, user_id)


@router.post("/waybill/{waybill_id}/offers", status_code=201, response_model=WaybillOfferSchema)
async def add_offer_to_waybill(
    waybill_id: UUID,
    waybill_offer: WaybillOfferPostSchema,
    db_session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    # получаем текущие данные из offers — для валидации
    offer = await OfferDAO.find_by_id(db_session, waybill_offer.offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    product: Product = offer.product
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    waybill_offer_obj = await WaybillService.add_offer_to_waybill(
        db_session, waybill_id, waybill_offer
    )

    return WaybillOfferSchema(
        id=waybill_offer_obj.id,
        waybill_id=waybill_id,
        offer_id=offer.id,
        quantity=waybill_offer_obj.quantity,
        brand=waybill_offer_obj.brand,
        manufacturer_number=waybill_offer_obj.manufacturer_number,
        price_rub=waybill_offer_obj.price_rub,
        product_name=product.name,
        image_url=product.image_url,
        category_slug=product.sub_category.category_slug,
        sub_category_slug=product.sub_category_slug,
    )


@router.delete("/waybill-offers/{waybill_offer_id}", status_code=204)
async def delete_offer_from_waybill(
    waybill_offer_id: UUID,
    db_session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    deleted = await WaybillOfferDAO.delete_by_id(db_session, waybill_offer_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Offer not found in waybill")
    return
