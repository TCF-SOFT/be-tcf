from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.dao.category_dao import CategoryDAO
from api.di.database import get_db
from common.deps.s3_service import get_s3_service
from common.exceptions.exceptions import DuplicateNameError
from common.functions.check_file_mime_type import is_file_mime_type_correct
from common.services.s3_service import S3Service
from schemas.category_schema import (
    CategoryPostSchema,
    CategoryPutSchema,
    CategorySchema,
)
from utils.logging import logger

router = APIRouter(tags=["Category"])


@router.get(
    "/categories",
    response_model=list[CategorySchema],
    summary="",
    status_code=status.HTTP_200_OK,
)
# @cache(expire=60 * 10, coder=ORJsonCoder)
async def get_categories(
    db_session: AsyncSession = Depends(get_db),
    slug: str = None,
    count_only: bool = False,
    order_by: str = None,
):
    filters = {}
    if slug:
        filters["slug"] = slug

    return await CategoryDAO.find_all(db_session, filter_by=filters, order_by=order_by)


@router.get(
    "/category/{slug}", response_model=CategorySchema, status_code=status.HTTP_200_OK
)
async def get_category_by_slug(
    slug: str,
    db_session: AsyncSession = Depends(get_db),
):
    return await CategoryDAO.find_by_slug(db_session, slug)


@router.post(
    "/category", response_model=CategorySchema, status_code=status.HTTP_201_CREATED
)
async def post_category(
    category: CategoryPostSchema,
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

    image_key: Annotated[str, "folder/<uuid>.ext"] = await s3.upload_file(
        image_blob.file,
        image_blob.filename,
        remote_path="images/categories",
        extra_args={"ACL": "public-read", "ContentType": image_blob.content_type},
    )

    category.image_url = s3.get_file_url(key=image_key)

    try:
        return await CategoryDAO.add(db_session, **category.model_dump())

    except DuplicateNameError as e:
        await s3.remove_file(image_key)
        logger.warning(
            f"Attempt to create a category with existing slug/name: {category.name}"
        )
        raise e


@router.put(
    "/category/{category_id}",
    response_model=int,
    summary="Update category by id",
    status_code=status.HTTP_200_OK,
)
async def put_category(
    category_id: UUID,
    category: CategoryPutSchema,
    image_blob: UploadFile | None = File(None),
    db_session: AsyncSession = Depends(get_db),
    s3: S3Service = Depends(get_s3_service),
):
    filters = {"id": category_id}
    image_key: str | None = None
    payload = category.model_dump(exclude_unset=True)

    if image_blob:
        try:
            await is_file_mime_type_correct(image_blob)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"File contents don’t match the file extension: {e}",
            )

        image_key: Annotated[str, "folder/<uuid>.ext"] = await s3.upload_file(
            image_blob.file,
            image_blob.filename,
            remote_path="images/categories",
            extra_args={"ACL": "public-read", "ContentType": image_blob.content_type},
        )
        payload["image_url"] = s3.get_file_url(key=image_key)

    try:
        res: Annotated[int, "affected rows"] = await CategoryDAO.update(
            db_session, filters, **payload
        )
    except DuplicateNameError as e:
        if image_key:
            await s3.remove_file(image_key)
        logger.warning(
            f"Attempt to create a category with existing slug/name: {category.name}"
        )
        raise e

    if not res:
        raise HTTPException(status_code=404, detail="Category not found")
    return res


@router.delete(
    "/category/{category_id}",
    summary="Delete a category by id",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_category(
    category_id: UUID,
    db_session: AsyncSession = Depends(get_db),
):
    success = await CategoryDAO.delete_by_id(db_session, category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
