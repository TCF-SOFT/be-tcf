from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi_cache.decorator import cache
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status

from api.dao.product_dao import ProductDAO
from api.di.database import get_db
from schemas.schemas import ProductSchema, ProductPostSchema, ProductPutSchema
from utils.cache_coder import ORJsonCoder

# Create the router
router = APIRouter(tags=["Products"])


@router.get(
    "/products",
    response_model=Page[ProductSchema],
    summary="Return all products with pagination or filter them",
    status_code=status.HTTP_200_OK
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
    status_code=status.HTTP_200_OK
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
    summary="Full text search products",
    status_code=status.HTTP_200_OK
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
    summary="Semantic/Vector search products by name",
    status_code=status.HTTP_200_OK
)
@cache(expire=60, coder=ORJsonCoder)
async def semantic_search_products(
    search_term: str,
    db_session: AsyncSession = Depends(get_db),
):
    return await ProductDAO.vector_search(db_session, search_term)


@router.get(
    "/product/{product_id}",
    response_model=ProductSchema,
    summary="Return product by id",
    status_code=status.HTTP_200_OK
)
async def get_product(
    product_id: UUID,
    db_session: AsyncSession = Depends(get_db),
):
    return await ProductDAO.find_by_id(db_session, product_id)



@router.post("/product",
             response_model=ProductSchema,
             summary="Create new product",
             status_code=status.HTTP_201_CREATED)
async def post_product(
    product: ProductPostSchema,
    db_session: AsyncSession = Depends(get_db),
):
    return await ProductDAO.add(db_session, **product.model_dump())


@router.put("/product/{product_id}",
            response_model=int,
            summary="Update product by id",
            status_code=status.HTTP_200_OK)
async def put_product(
    product_id: UUID,
    product: ProductPutSchema,
    db_session: AsyncSession = Depends(get_db),
):
    filters = {"id": product_id}

    res: Annotated[int, "affected rows"]  = await ProductDAO.update(db_session, filters, **product.model_dump())

    if not res:
        raise HTTPException(status_code=404, detail="Product not found")

    return res

@router.delete(
    "/products/{product_id}", summary="Delete product by id", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_product(
    product_id: UUID,
    db_session: AsyncSession = Depends(get_db),
):
    success = await ProductDAO.delete_by_id(db_session, product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")