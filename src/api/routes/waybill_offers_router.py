from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dao.waybill_offer_dao import WaybillOfferDAO
from src.api.di.database import get_db

router = APIRouter(tags=["Waybill-Offers"], prefix="/waybill-offers")


@router.delete("/{waybill_offer_id}", status_code=204)
async def delete_offer_from_waybill(
    waybill_offer_id: UUID,
    db_session: AsyncSession = Depends(get_db),
    # user=Depends(get_current_user),
):
    deleted = await WaybillOfferDAO.delete_by_id(db_session, waybill_offer_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Offer not found in waybill")
    return
