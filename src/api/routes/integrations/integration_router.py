from datetime import datetime
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, Depends, Response
from fastapi.responses import FileResponse
from fastapi_cache.decorator import cache
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.integrations import build_yml
from src.api.di.db_helper import db_helper
from src.utils.cache_coder import ORJsonCoder

router = APIRouter(tags=["Integrations"], prefix="/integrations")


# --------------------------------------------------------
# Endpoint 1 — normal Yandex feed (for production)
# --------------------------------------------------------
@cache(expire=3600 * 12, coder=ORJsonCoder)
@router.get("/yml", response_class=Response)
async def export_yml(db: AsyncSession = Depends(db_helper.session_getter)):
    xml = await build_yml(db)
    return Response(content=xml, media_type="application/xml")


# --------------------------------------------------------
# Endpoint 2 — downloadable file for debugging
# --------------------------------------------------------
@router.get("/yml/file")
async def export_yml_file(db: AsyncSession = Depends(db_helper.session_getter)):
    xml = await build_yml(db)

    with NamedTemporaryFile(delete=False, suffix=".xml") as tmp:
        tmp.write(xml.encode("utf-8"))

    return FileResponse(
        tmp.name,
        media_type="application/xml",
        filename=f"yml_feed_{datetime.now().date()}.xml",
    )
