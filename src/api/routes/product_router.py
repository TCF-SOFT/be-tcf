from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi_cache.decorator import cache
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio import AsyncSession

from api.dao.product_dao import ProductDAO
from api.di.database import get_db
from schemas.schemas import ProductSchema, ProductPostSchema
from utils.cache_coder import ORJsonCoder

# Create the router
router = APIRouter(tags=["Products"])


@router.get(
    "/products",
    response_model=Page[ProductSchema],
    summary="Return all products with pagination or filter them",
)
@cache(expire=60, coder=ORJsonCoder)
async def search_products(
    db_session: AsyncSession = Depends(get_db),
    sub_category_id: UUID | None = None,
    sub_category_slug: str | None = None,
):
    filters = {}
    if sub_category_id:
        filters["sub_category_id"] = sub_category_id

    if sub_category_slug:
        filters["sub_category_slug"] = sub_category_slug

    return await ProductDAO.find_all(db_session, filter_by=filters)


@router.get(
    "/products/search",
    response_model=Page[ProductSchema],
    summary="Search products by name",
)
@cache(expire=60, coder=ORJsonCoder)
async def search_products_by_name(
    search_term: str,
    db_session: AsyncSession = Depends(get_db),
):
    return await ProductDAO.wildcard_search(db_session, search_term)


@router.get(
    "/products/text_search",
    response_model=Page[ProductSchema],
    summary="Search products by name",
)
@cache(expire=60, coder=ORJsonCoder)
async def full_text_search_products(
    search_term: str,
    db_session: AsyncSession = Depends(get_db),
):
    return await ProductDAO.full_text_search(db_session, search_term)


@router.get(
    "/products/vector_search",
    response_model=Page[ProductSchema],
    summary="Search products by name",
)
@cache(expire=60, coder=ORJsonCoder)
async def semantic_search_products(
    search_term: str,
    db_session: AsyncSession = Depends(get_db),
):
    return await ProductDAO.vector_search(db_session, search_term)


@router.get(
    "/products/{product_id}",
    response_model=ProductSchema,
    summary="Return product by id",
)
@cache(expire=60, coder=ORJsonCoder)
async def get_product(
    product_id: UUID,
    db_session: AsyncSession = Depends(get_db),
):
    return await ProductDAO.find_by_id(db_session, product_id)



@router.post("/product", response_model=ProductSchema, status_code=201)
async def post_product(
    product: ProductPostSchema,
    db_session: AsyncSession = Depends(get_db),
):
    return await ProductDAO.add(db_session, **product.model_dump())



@router.delete(
    "/products/{product_id}", status_code=204
)
async def delete_product(
    product_id: UUID,
    db_session: AsyncSession = Depends(get_db),
):
    success = await ProductDAO.delete_by_id(db_session, product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")