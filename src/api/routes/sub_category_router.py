from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.dao.sub_category_dao import SubCategoryDAO
from api.di.database import get_db
from schemas.schemas import SubCategorySchema

# Create the router
router = APIRouter(tags=["Sub-Category"])


@router.get(
    "/sub-categories",
    response_model=list[SubCategorySchema],
    summary="",
)
async def get_sub_categories(
    db_session: AsyncSession = Depends(get_db),
    slug: str = None,
    category_id: UUID | None = None,
    category_slug: str = None,
):
    filters = {}
    if slug:
        filters["slug"] = slug
    if category_id:
        filters["category_id"] = category_id
    if category_slug:
        filters["category_slug"] = category_slug

    return await SubCategoryDAO.find_all(db_session, filter_by=filters)
