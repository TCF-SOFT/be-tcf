from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi_cache.decorator import cache, logger
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.controllers.update_entity_controller import update_entity_with_optional_image
from api.dao.category_dao import CategoryDAO
from api.dao.sub_category_dao import SubCategoryDAO
from api.di.database import get_db
from common.deps.s3_service import get_s3_service
from common.exceptions.exceptions import DuplicateNameError
from common.functions.check_file_mime_type import is_file_mime_type_correct
from common.services.s3_service import S3Service
from schemas.category_schema import CategorySchema
from schemas.sub_category_schema import (
    SubCategoryPostSchema,
    SubCategoryPutSchema,
    SubCategorySchema,
)
from utils.cache_coder import ORJsonCoder

router = APIRouter(tags=["Sub-Category"])


@router.get(
    "/sub-categories",
    response_model=list[SubCategorySchema],
    summary="",
    status_code=status.HTTP_200_OK,
)
@cache(expire=60 * 10, coder=ORJsonCoder)
async def get_sub_categories(
    db_session: AsyncSession = Depends(get_db),
    category_id: UUID | None = None,
    category_slug: str = None
):
    filters = {}
    if category_slug:
        category: CategorySchema = await CategoryDAO.find_by_slug(db_session, category_slug)
        filters["category_id"] = category.id
    if category_id:
        filters["category_id"] = category_id

    return await SubCategoryDAO.find_all(db_session, filter_by=filters)


@router.get(
    "/sub-category/{slug}",
    response_model=SubCategorySchema,
    status_code=status.HTTP_200_OK,
)
async def get_sub_category_by_slug(
    slug: str,
    db_session: AsyncSession = Depends(get_db),
):
    return await SubCategoryDAO.find_by_slug(db_session, slug)


@router.post(
    "/sub-category",
    response_model=SubCategorySchema,
    status_code=status.HTTP_201_CREATED,
)
async def post_sub_category(
    sub_category: SubCategoryPostSchema,
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
    sub_category.image_url = s3.get_file_url(key=image_key)
    try:
        res = await SubCategoryDAO.add(
            **sub_category.model_dump(), db_session=db_session
        )
        # Два решения: добавлять в ответ или использовать lazy=joined и делать refresh
        # category = await CategoryDAO.find_by_id(db_session, sub_category.category_id)
        # return SubCategorySchema.model_validate(
        #     res, from_attributes=True
        # ).model_copy(update={"category_slug": category.slug})
        await db_session.refresh(res, ["category"])
        await s3.upload_file(
            file=image_blob.file,
            key=image_key,
            extra_args={"ACL": "public-read", "ContentType": image_blob.content_type},
        )
        return res
    except DuplicateNameError as e:
        logger.warning(
            f"Attempt to create a sub_category with existing slug: {sub_category.slug}"
        )
        raise e


@router.put(
    "/sub-category/{sub_category_id}",
    response_model=SubCategorySchema,
    summary="Update a sub_category by id",
    status_code=status.HTTP_200_OK,
)
async def put_sub_category(
    sub_category_id: UUID,
    sub_category: SubCategoryPutSchema,
    image_blob: UploadFile | None = File(None),
    db_session: AsyncSession = Depends(get_db),
    s3: S3Service = Depends(get_s3_service),
):
    return await update_entity_with_optional_image(
        entity_id=sub_category_id,
        payload=sub_category,
        dao=SubCategoryDAO,
        upload_path="images/sub_categories",
        db_session=db_session,
        s3=s3,
        image_blob=image_blob,
    )


@router.delete(
    "/sub-category/{sub_category_id}",
    summary="Delete sub_category by id",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_sub_category(
    sub_category_id: UUID,
    db_session: AsyncSession = Depends(get_db),
):
    success = await SubCategoryDAO.delete_by_id(db_session, sub_category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Sub Category not found")
