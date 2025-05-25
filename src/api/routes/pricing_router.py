from io import BytesIO
from typing import Literal, Any, Coroutine

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import StreamingResponse
from starlette.responses import StreamingResponse

from api.controllers.pricing_controller import generate_price
from api.di.database import get_db

router = APIRouter(tags=["Pricing"])


@router.get("/price/{pricing_type}", status_code=200)
async def get_price(
    pricing_type: Literal["retail", "wholesale"],
    db_session: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    data: BytesIO = await generate_price(pricing_type, db_session)
    return StreamingResponse(
        data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=export.xlsx"},
    )
