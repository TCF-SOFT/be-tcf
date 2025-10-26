from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth.clerk import require_role
from src.api.core.update_entity import update_entity
from src.api.dao.waybill_offer_dao import WaybillOfferDAO
from src.api.di.db_helper import db_helper
from src.schemas.common.enums import Role
from src.schemas.waybill_offer_schema import WaybillOfferPatchSchema, WaybillOfferSchema

router = APIRouter(
    tags=["Waybill-Offers"],
    prefix="/waybill-offers",
    dependencies=[Depends(require_role(Role.EMPLOYEE))],
)


@router.patch(
    "/{waybill_offer_id}",
    status_code=status.HTTP_200_OK,
    response_model=WaybillOfferSchema,
)
async def update_offer_in_waybill(
    waybill_offer_id: UUID,
    payload: WaybillOfferPatchSchema,
    db_session: AsyncSession = Depends(db_helper.session_getter),
):
    return await update_entity(
        entity_id=waybill_offer_id,
        payload=payload,
        dao=WaybillOfferDAO,
        db_session=db_session,
    )


@router.delete("/{waybill_offer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_offer_from_waybill(
    waybill_offer_id: UUID,
    db_session: AsyncSession = Depends(db_helper.session_getter),
):
    deleted = await WaybillOfferDAO.delete_by_id(db_session, waybill_offer_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Offer not found in waybill"
        )
    return
