from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio import AsyncSession

from api.dao.product_dao import ProductDAO
from api.di.database import get_db
from schemas.schemas import ProductSchema
from schemas.enums import Categories

# Create the router
router = APIRouter(tags=["Products"])


@router.get(
    "/products",
    response_model=Page[ProductSchema],
    summary="Return all products with pagination or filter them",
)
async def search_products(
    db_session: AsyncSession = Depends(get_db),
    category: Categories = None,
):
    filters = {}
    if category:
        filters["category"] = category

    return await ProductDAO.find_all(db_session, filter_by=filters)


@router.get("/products/categories", response_model=list[str])
async def get_product_categories(
    db_session: AsyncSession = Depends(get_db),
):
    """
    Get all product categories
    """
    categories = await ProductDAO.find_categories(db_session, filter_by={})
    return categories


@router.get("/products/sub-categories", response_model=list[str])
async def get_product_sub_categories(
    db_session: AsyncSession = Depends(get_db),
):
    """
    Get all product sub-categories
    """
    sub_categories = await ProductDAO.find_sub_categories(db_session, filter_by={})
    return sub_categories
