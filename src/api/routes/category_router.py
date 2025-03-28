from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.dao.category_dao import CategoryDAO
from api.di.database import get_db
from schemas.schemas import CategorySchema

# Create the router
router = APIRouter(tags=["Category"])


@router.get(
    "/categories",
    response_model=list[CategorySchema],
    summary="",
)
async def get_categories(
    db_session: AsyncSession = Depends(get_db),
):
    filters = {}
    return await CategoryDAO.find_all(db_session, filter_by=filters)
