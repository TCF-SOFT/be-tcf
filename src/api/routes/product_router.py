from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi_cache.decorator import cache
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio import AsyncSession

from api.controllers.update_entity_controller import update_entity_with_optional_image
from api.dao.product_dao import ProductDAO
from api.dao.sub_category_dao import SubCategoryDAO
from api.di.database import get_db
from common.deps.s3_service import get_s3_service
from common.exceptions.exceptions import DuplicateNameError
from common.functions.check_file_mime_type import is_file_mime_type_correct
from common.services.s3_service import S3Service
from schemas.product_schema import ProductPostSchema, ProductPutSchema, ProductSchema
from schemas.sub_category_schema import SubCategorySchema
from utils.cache_coder import ORJsonCoder
from utils.logging import logger

router = APIRouter(tags=["Products"])


@router.get(
    "/products",
    response_model=Page[ProductSchema],
    summary="Return all products with pagination or filter them",
    status_code=status.HTTP_200_OK,
)
# @cache(expire=60, coder=ORJsonCoder)
async def get_products(
    db_session: AsyncSession = Depends(get_db),
    sub_category_id: UUID | None = None,
    sub_category_slug: str | None = None,
):
    filters = {}
    if sub_category_slug:
        sub_category: SubCategorySchema = await SubCategoryDAO.find_by_slug(
            db_session, sub_category_slug
        )
        filters["sub_category_slug"] = sub_category.slug
    if sub_category_id:
        filters["sub_category_id"] = sub_category_id

    return await ProductDAO.find_all(db_session, filter_by=filters)


@router.get(
    "/products/search",
    response_model=Page[ProductSchema],
    summary="Search products by name",
    status_code=status.HTTP_200_OK,
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
    status_code=status.HTTP_200_OK,
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
    status_code=status.HTTP_200_OK,
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
    status_code=status.HTTP_200_OK,
)
async def get_product(
    product_id: UUID,
    db_session: AsyncSession = Depends(get_db),
):
    return await ProductDAO.find_by_id(db_session, product_id)


@router.post(
    "/product",
    response_model=ProductSchema,
    summary="Create new product",
    status_code=status.HTTP_201_CREATED,
)
async def post_product(
    product: ProductPostSchema,
    image_blob: UploadFile = File(...),
    db_session: AsyncSession = Depends(get_db),
    s3: S3Service = Depends(get_s3_service),
):
    try:
        await is_file_mime_type_correct(image_blob)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File contents don’t match the file extension: {e}",
        )

    image_key: Annotated[str, "folder/<uuid>.ext"] = s3.generate_key(
        image_blob.filename, "images/sub_categories"
    )
    product.image_url = s3.get_file_url(key=image_key)
    try:
        res = await ProductDAO.add(**product.model_dump(), db_session=db_session)
        await db_session.refresh(res, ["sub_category"])
        await s3.upload_file(
            file=image_blob.file,
            key=image_key,
            extra_args={"ACL": "public-read", "ContentType": image_blob.content_type},
        )
        return res
    except DuplicateNameError as e:
        logger.warning(
            f"Attempt to create a product with existing slug: {product.slug}"
        )
        raise e


@router.put(
    "/product/{product_id}",
    response_model=ProductSchema,
    summary="Update product by id",
    status_code=status.HTTP_200_OK,
)
async def put_product(
    product_id: UUID,
    product: ProductPutSchema,
    image_blob: UploadFile | None = File(None),
    db_session: AsyncSession = Depends(get_db),
    s3: S3Service = Depends(get_s3_service),
):
    return await update_entity_with_optional_image(
        entity_id=product_id,
        payload=product,
        dao=ProductDAO,
        upload_path="images/tmp",
        db_session=db_session,
        s3=s3,
        image_blob=image_blob,
    )


@router.delete(
    "/product/{product_id}",
    summary="Delete product by id",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_product(
    product_id: UUID,
    db_session: AsyncSession = Depends(get_db),
):
    success = await ProductDAO.delete_by_id(db_session, product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
