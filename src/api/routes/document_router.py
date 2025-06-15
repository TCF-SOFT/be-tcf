from pathlib import Path
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import FileResponse

from api.controllers.pricing_controller import generate_price, serve_price
from api.dao.waybill_dao import WaybillDAO
from api.di.database import get_db
from api.services.waybill_service import WaybillService
from new_print import InvoiceGenerator
from schemas.waybill_offer_schema import WaybillOfferSchema
from schemas.waybill_schema import WaybillSchema
from tasks.mailing import send_pricing_email

router = APIRouter(tags=["Documents"], prefix="/documents")


@router.get(
    "/waybills/{waybill_id}/print",
    status_code=status.HTTP_200_OK,
    response_model=FileResponse,
)
async def print_waybill(
    waybill_id: UUID,
    printer: InvoiceGenerator = Depends(InvoiceGenerator),
    db_session: AsyncSession = Depends(get_db),
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
            detail="Can't generate PDF",
        )

    invoice_data = {
    "number": "51240 13793277",
    "fio": "2 Менеджер",
    "phone": "+7 (999) 042-46-66",
    "city": "Не заполнен у пользователя",
    "delivery": "Самовывоз",
    "items": [
        {"name": "Прокладки клапанной крышки", "brand": "Transit BSG", "number": "AR893", "price": 500, "quantity": 10},
        {"name": "Прокладки клапанной крышки", "brand": "Transit пробка", "number": "AR806", "price": 300, "quantity": 5}
    ],
    "total": 9999
}


    return FileResponse(
        path=printer.create_invoice(invoice_data),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f"attachment; filename=waybill_{waybill_id}.docx"
        },
    )


@router.get(
    "/price/{price_type}", status_code=status.HTTP_200_OK, response_class=FileResponse
)
async def get_price(
    price_type: Literal["retail", "wholesale"],
    ext: Literal["xlsx", "csv"],
    cache: bool = True,
) -> FileResponse:
    """
    Get the price list in the specified format.
    CSV: 5.0mb
    XLSX: 1.8mb
    """
    path: Path = (
        await serve_price(price_type, ext)
        if cache
        else await generate_price(price_type, ext)
    )
    return FileResponse(
        path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        if ext == "xlsx"
        else "text/csv",
        filename=f"price.{ext}" if price_type == "retail" else "price_wholesale.csv",
    )


@router.post("/send/{email}", status_code=status.HTTP_201_CREATED)
async def send_price_email(
    price_type: Literal["retail", "wholesale"],
    ext: Literal["xlsx", "csv"],
    email: EmailStr,
    background_tasks: BackgroundTasks,
) -> None:
    """
    Send the price list to the email.
    """
    background_tasks.add_task(send_pricing_email, email)
