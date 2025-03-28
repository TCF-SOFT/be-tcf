from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio import AsyncSession

from api.dao.product_dao import ProductDAO
from api.di.database import get_db
from schemas.schemas import ProductSchema

# Create the router
router = APIRouter(tags=["Products"])


@router.get(
    "/products",
    response_model=Page[ProductSchema],
    summary="Return all products with pagination or filter them",
)
async def search_products(
    db_session: AsyncSession = Depends(get_db),
    sub_category_id: UUID | None = None,
):
    filters = {}
    if sub_category_id:
        filters["sub_category_id"] = sub_category_id  # <- correct field name

    return await ProductDAO.find_all(db_session, filter_by=filters)
