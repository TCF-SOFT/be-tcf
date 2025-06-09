from pathlib import Path
from typing import Literal

from fastapi import APIRouter, BackgroundTasks, status
from pydantic import EmailStr
from starlette.responses import FileResponse

from api.controllers.pricing_controller import generate_price, serve_price
from tasks.mailing import send_pricing_email

router = APIRouter(tags=["Pricing"], prefix="/pricing")


@router.get("/{price_type}", status_code=status.HTTP_200_OK, response_class=FileResponse)
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
