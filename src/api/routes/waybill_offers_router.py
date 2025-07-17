from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.clerk import require_clerk_session
from src.api.dao.waybill_offer_dao import WaybillOfferDAO
from src.api.di.db_helper import db_helper

router = APIRouter(
    tags=["Waybill-Offers"],
    prefix="/waybill-offers",
    dependencies=[Depends(require_clerk_session)],
)


@router.delete("/{waybill_offer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_offer_from_waybill(
    waybill_offer_id: UUID,
    db_session: AsyncSession = Depends(db_helper.session_getter),
    # user=Depends(get_current_user),
):
    deleted = await WaybillOfferDAO.delete_by_id(db_session, waybill_offer_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Offer not found in waybill"
        )
    return
