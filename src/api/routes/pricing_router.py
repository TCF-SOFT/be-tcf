from pathlib import Path
from typing import Literal

from fastapi import APIRouter
from starlette.responses import FileResponse

from api.controllers.pricing_controller import generate_price, serve_price

router = APIRouter(tags=["Pricing"])


@router.get("/price/{price_type}", status_code=200, response_class=FileResponse)
async def get_price(
    price_type: Literal["retail", "wholesale"], ext: Literal["xlsx", "csv"], cache: bool = True,
) -> FileResponse:
    """
    Get the price list in the specified format.
    CSV: 5.0mb
    XLSX: 1.8mb
    """
    path: Path = await serve_price(price_type, ext) if cache else await generate_price(price_type, ext)
    return FileResponse(
        path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        if ext == "xlsx"
        else "text/csv",
        filename=f"price.{ext}" if price_type == "retail" else "price_wholesale.csv",
    )
