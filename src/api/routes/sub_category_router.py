from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi_cache.decorator import cache
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.dao.sub_category_dao import SubCategoryDAO
from api.di.database import get_db
from schemas.schemas import CountSchema, SubCategorySchema
from utils.cache_coder import ORJsonCoder

# Create the router
router = APIRouter(tags=["Sub-Category"])


@router.get(
    "/sub-categories",
    response_model=list[SubCategorySchema] | CountSchema,
    summary="",
    status_code=status.HTTP_200_OK
)
@cache(expire=60 * 10, coder=ORJsonCoder)
async def get_sub_categories(
    db_session: AsyncSession = Depends(get_db),
    slug: str = None,
    category_id: UUID | None = None,
    category_slug: str = None,
    count_only: bool = False,
):
    filters = {}
    if slug:
        filters["slug"] = slug
    if category_id:
        filters["category_id"] = category_id
    if category_slug:
        filters["category_slug"] = category_slug

    if count_only:
        return await SubCategoryDAO.count_all(db_session, filter_by=filters)

    return await SubCategoryDAO.find_all(db_session, filter_by=filters)


@router.get(
    "/sub-category/{slug}",
    response_model=SubCategorySchema,
    status_code=status.HTTP_200_OK
)
async def get_category_by_slug(
    slug: str,
    db_session: AsyncSession = Depends(get_db),
):
    return await SubCategoryDAO.find_by_slug(db_session, slug)
