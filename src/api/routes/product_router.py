from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.controllers.create_entity_controller import create_entity_with_image
from src.api.controllers.update_entity_controller import (
    update_entity_with_optional_image,
)
from src.api.dao.product_dao import ProductDAO
from src.api.dao.sub_category_dao import SubCategoryDAO
from src.api.di.db_helper import db_helper
from src.api.routes.clerk import require_clerk_session
from src.common.deps.s3_service import get_s3_service
from src.common.services.s3_service import S3Service
from src.schemas.product_schema import (
    ProductPostSchema,
    ProductPutSchema,
    ProductSchema,
)
from src.schemas.sub_category_schema import SubCategorySchema

router = APIRouter(tags=["Products"], prefix="/products")


@router.get(
    "",
    response_model=Page[ProductSchema],
    summary="Return all products with pagination or filter them",
    status_code=status.HTTP_200_OK,
)
# @cache(expire=60, coder=ORJsonCoder)
async def get_products(
    db_session: AsyncSession = Depends(db_helper.session_getter),
    sub_category_id: UUID | None = None,
    sub_category_slug: str | None = None,
    is_deleted: bool = False,
):
    filters: dict[str, bool | UUID | str] = {"is_deleted": is_deleted}
    if sub_category_slug:
        sub_category: SubCategorySchema = await SubCategoryDAO.find_by_slug(
            db_session, sub_category_slug
        )
        if sub_category:
            filters["sub_category_id"] = sub_category.id

    if sub_category_id:
        filters["sub_category_id"] = sub_category_id

    return await ProductDAO.find_all_paginate(db_session, filter_by=filters)


@router.get(
    "/{product_id}",
    response_model=ProductSchema,
    summary="Return product by id",
    status_code=status.HTTP_200_OK,
)
async def get_product_by_id(
    product_id: UUID,
    db_session: AsyncSession = Depends(db_helper.session_getter),
):
    res = await ProductDAO.find_by_id(db_session, product_id)
    if not res:
        raise HTTPException(status_code=404, detail="Product not found")
    return res


@router.get(
    "/slug/{slug}",
    response_model=ProductSchema,
    summary="Return product by slug",
    status_code=status.HTTP_200_OK,
)
async def get_product_by_slug(
    slug: UUID,
    db_session: AsyncSession = Depends(db_helper.session_getter),
):
    res = await ProductDAO.find_by_slug(db_session, slug)
    if not res:
        raise HTTPException(status_code=404, detail="Product not found")
    return res


@router.get(
    "/search",
    response_model=Page[ProductSchema],
    summary="Search products by name",
    status_code=status.HTTP_200_OK,
)
async def search_products_by_name(
    search_term: str,
    db_session: AsyncSession = Depends(db_helper.session_getter),
):
    return await ProductDAO.wildcard_search(db_session, search_term)


@router.get(
    "/text_search",
    response_model=Page[ProductSchema],
    summary="Full text search products",
    status_code=status.HTTP_200_OK,
)
async def full_text_search_products(
    search_term: str,
    db_session: AsyncSession = Depends(db_helper.session_getter),
):
    return await ProductDAO.full_text_search(db_session, search_term)


# @router.get(
#     "/products/vector_search",
#     response_model=Page[ProductSchema],
#     summary="Semantic/Vector search products by name",
#     status_code=status.HTTP_200_OK,
# )
# @cache(expire=60, coder=ORJsonCoder)
# async def semantic_search_products(
#     search_term: str,
#     db_session: AsyncSession = Depends(db_helper.session_getter),
# ):
#     return await ProductDAO.vector_search(db_session, search_term)


@router.post(
    "",
    response_model=ProductSchema,
    summary="Create new product",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_clerk_session)],
)
async def post_product(
    payload: Annotated[ProductPostSchema, Depends(ProductPostSchema.as_form)],
    image_blob: UploadFile = File(...),
    db_session: AsyncSession = Depends(db_helper.session_getter),
    s3: S3Service = Depends(get_s3_service),
):
    return await create_entity_with_image(
        payload=payload,
        image_blob=image_blob,
        upload_path="images/tmp",
        db_session=db_session,
        s3=s3,
        dao=ProductDAO,
        refresh_fields=["sub_category"],
    )


@router.patch(
    "/{product_id}",
    response_model=ProductSchema,
    summary="Update product by id",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_clerk_session)],
)
async def patch_product(
    product_id: UUID,
    payload: Annotated[ProductPutSchema, Depends(ProductPutSchema.as_form)],
    image_blob: UploadFile | None = File(None),
    db_session: AsyncSession = Depends(db_helper.session_getter),
    s3: S3Service = Depends(get_s3_service),
):
    return await update_entity_with_optional_image(
        entity_id=product_id,
        payload=payload,
        dao=ProductDAO,
        upload_path="images/tmp",
        db_session=db_session,
        s3=s3,
        image_blob=image_blob,
    )


@router.delete(
    "/{product_id}",
    summary="Delete product by id",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_clerk_session)],
)
async def delete_product(
    product_id: UUID,
    db_session: AsyncSession = Depends(db_helper.session_getter),
):
    success = await ProductDAO.delete_by_id(db_session, product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
