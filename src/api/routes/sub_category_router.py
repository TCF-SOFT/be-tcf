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
    category_id: UUID = None,
):
    filters = {"category_id": category_id}
    return await SubCategoryDAO.find_all(db_session, filter_by=filters)
