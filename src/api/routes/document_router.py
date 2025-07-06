from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import FileResponse
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.controllers.pricing_controller import generate_price, serve_price
from src.api.dao.waybill_dao import WaybillDAO
from src.api.di.db_helper import db_helper
from src.api.services.waybill_service import WaybillService
from src.schemas.common.enums import PriceListExt, PriceListType
from src.schemas.waybill_offer_schema import WaybillOfferSchema
from src.schemas.waybill_schema import WaybillSchema
from src.tasks.mailing import send_pricing_email
from src.tasks.waybills.print_waybill import create_document

router = APIRouter(tags=["Documents"], prefix="/documents")


@router.get(
    "/waybills/{waybill_id}/print",
    status_code=status.HTTP_200_OK,
)
async def print_waybill(
    waybill_id: UUID,
    # printer: InvoiceGenerator = Depends(InvoiceGenerator),
    db_session: AsyncSession = Depends(db_helper.session_getter),
):
    waybill_raw = await WaybillDAO.find_by_id(db_session, waybill_id)
    if not waybill_raw:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Waybill not found"
        )
    offers_raw = await WaybillService.fetch_waybill_offers(waybill_raw)

    try:
        waybill = WaybillSchema.model_validate(waybill_raw)
        offers = [WaybillOfferSchema.model_validate(o) for o in offers_raw]
        total_sum = sum(o.price_rub * o.quantity for o in offers)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Can't generate Word",
        )

    return FileResponse(
        path=create_document(waybill, offers, total_sum),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


@router.get(
    "/price/{price_type}", status_code=status.HTTP_200_OK, response_class=FileResponse
)
async def get_price(
    price_type: PriceListType,
    ext: PriceListExt,
    cache: bool = True,
) -> FileResponse:
    """
    Get the price list in the specified format.
    CSV: 5.0mb
    XLSX: 1.8mb
    """
    if ext == PriceListExt.EXCEL:
        ext = "xlsx"
    else:
        ext = "csv"

    path: Path = (
        await serve_price(price_type, ext)
        if cache
        else await generate_price(price_type, ext)
    )
    return FileResponse(
        path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        if ext == PriceListExt.EXCEL
        else "text/csv",
        filename=f"price.{ext}" if price_type == "retail" else "price_wholesale.csv",
    )


@router.post("/send/{email}", status_code=status.HTTP_201_CREATED)
async def send_price_email(
    price_type: PriceListType,
    ext: PriceListExt,
    email: EmailStr,
    background_tasks: BackgroundTasks,
) -> None:
    """
    Send the price list to the email.
    """
    background_tasks.add_task(send_pricing_email, email)
