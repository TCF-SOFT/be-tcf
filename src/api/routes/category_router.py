from fastapi import APIRouter, Depends
from fastapi_cache.decorator import cache
from sqlalchemy.ext.asyncio import AsyncSession

from api.dao.category_dao import CategoryDAO
from api.di.database import get_db
from schemas.schemas import CategorySchema, CountSchema
from utils.cache_coder import ORJsonCoder

# Create the router
router = APIRouter(tags=["Category"])


@router.get(
    "/categories",
    response_model=list[CategorySchema] | CountSchema,
    summary="",
)
@cache(expire=60 * 10, coder=ORJsonCoder)
async def get_categories(
    db_session: AsyncSession = Depends(get_db),
    slug: str = None,
    count_only: bool = False,
):
    filters = {}
    if slug:
        filters["slug"] = slug

    if count_only:
        return await CategoryDAO.count_all(db_session, filter_by=filters)

    return await CategoryDAO.find_all(db_session, filter_by=filters)
