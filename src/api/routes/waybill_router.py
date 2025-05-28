import uuid
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dao.waybill_dao import WaybillDAO
from src.api.di.database import get_db
from src.api.services.waybill_service import WaybillService
from src.schemas.waybill_offer_schema import WaybillOfferPostSchema
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


@router.get("/waybill/in", status_code=200, response_model=WaybillSchema)
async def get_waybill_in(
    db_session: AsyncSession = Depends(get_db),
    user_id: UUID | None = None,
):
    """
    Get waybill in
    """
    filters = {"type": "in"}
    if user_id:
        filters["user_id"] = user_id
    return await WaybillDAO.find_all(db_session, filter_by=filters)


@router.get("/waybill/out", status_code=200)
async def get_waybill_out(
    db_session: AsyncSession = Depends(get_db), user_id: UUID | None = None
):
    """
    Get waybill out
    """
    filters = {"type": "out"}
    if user_id:
        filters["user_id"] = user_id
    return await WaybillDAO.find_all(db_session, filter_by=filters)


@router.get("/waybill/{waybill_id}", status_code=200, response_model=WaybillSchema)
async def get_waybill(
    waybill_id: UUID, db_session: AsyncSession = Depends(get_db)
) -> WaybillSchema | None:
    """
    Get waybill by ID
    """
    return await WaybillDAO.find_by_id(db_session, waybill_id)


def get_current_user():
    return uuid.UUID("b5fe5a3b-dfa2-43d3-a81e-34404d8f75d4")


@router.post("/waybill", status_code=201, response_model=WaybillSchema)
async def create_waybill(
    waybill: WaybillPostSchema,
    db_session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    return await WaybillDAO.add(db_session, **waybill.model_dump())


@router.post("/waybill/{waybill_id}/commit", status_code=201, response_model=WaybillSchema)
async def commit_waybill(
    waybill_id: UUID,
    db_session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    return await WaybillService.commit(db_session, waybill_id, user.id)


@router.post("/waybill/{waybill_id}/offers", status_code=201)
async def add_offer_to_waybill(
    waybill_id: UUID,
    waybill_offer: WaybillOfferPostSchema,
    db_session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    return await WaybillService.add_offer_to_waybill(db_session, waybill_id, waybill_offer)