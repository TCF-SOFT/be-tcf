from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi_cache.decorator import cache
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.auth.clerk import require_role
from schemas.common.enums import Role
from src.api.core.create_entity import create_entity_with_image
from src.api.core.update_entity import (
    update_entity_with_optional_image,
)
from src.api.dao.category_dao import CategoryDAO
from src.api.dao.sub_category_dao import SubCategoryDAO
from src.api.di.db_helper import db_helper
from src.common.deps.s3_service import get_s3_service
from src.common.services.s3_service import S3Service
from src.schemas.category_schema import CategorySchema
from src.schemas.sub_category_schema import (
    SubCategoryPostSchema,
    SubCategoryPutSchema,
    SubCategorySchema,
)
from src.utils.cache_coder import ORJsonCoder

router = APIRouter(tags=["Sub-Categories"], prefix="/sub-categories")


@router.get(
    "",
    response_model=Page[SubCategorySchema],
    summary="Return all sub-categories with pagination or filter them",
    status_code=status.HTTP_200_OK,
)
@cache(expire=60 * 10, coder=ORJsonCoder)
async def get_sub_categories(
    db_session: AsyncSession = Depends(db_helper.session_getter),
    category_id: UUID | None = None,
    category_slug: str | None = None,
):
    filters = {}
    if category_slug:
        category: CategorySchema | None = await CategoryDAO.find_by_slug(
            db_session, category_slug
        )
        if category:
            filters["category_id"] = category.id
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )
    if category_id:
        filters["category_id"] = category_id

    return await SubCategoryDAO.find_all_paginate(db_session, filter_by=filters)


@router.get(
    "/{sub_category_id}",
    response_model=SubCategorySchema,
    status_code=status.HTTP_200_OK,
)
async def get_sub_category_by_id(
    sub_category_id: UUID,
    db_session: AsyncSession = Depends(db_helper.session_getter),
):
    res = await SubCategoryDAO.find_by_id(db_session, sub_category_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sub Category not found"
        )
    return res


@router.get(
    "/slug/{slug}",
    response_model=SubCategorySchema,
    status_code=status.HTTP_200_OK,
)
async def get_sub_category_by_slug(
    slug: str,
    db_session: AsyncSession = Depends(db_helper.session_getter),
):
    res = await SubCategoryDAO.find_by_slug(db_session, slug)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sub Category not found"
        )
    return res


@router.post(
    "",
    response_model=SubCategorySchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(Role.EMPLOYEE))],
)
async def post_sub_category(
    payload: Annotated[SubCategoryPostSchema, Depends(SubCategoryPostSchema.as_form)],
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
        dao=SubCategoryDAO,
        refresh_fields=["category"],
    )


@router.patch(
    "/{sub_category_id}",
    response_model=SubCategorySchema,
    summary="Update a sub_category by id",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_role(Role.EMPLOYEE))],
)
async def patch_sub_category(
    sub_category_id: UUID,
    payload: Annotated[SubCategoryPutSchema, Depends(SubCategoryPutSchema.as_form)],
    image_blob: UploadFile | None = File(None),
    db_session: AsyncSession = Depends(db_helper.session_getter),
    s3: S3Service = Depends(get_s3_service),
):
    return await update_entity_with_optional_image(
        entity_id=sub_category_id,
        payload=payload,
        dao=SubCategoryDAO,
        upload_path="images/sub_categories",
        db_session=db_session,
        s3=s3,
        image_blob=image_blob,
    )


@router.delete(
    "/{sub_category_id}",
    summary="Delete sub_category by id",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
async def delete_sub_category(
    sub_category_id: UUID,
    db_session: AsyncSession = Depends(db_helper.session_getter),
):
    success = await SubCategoryDAO.delete_by_id(db_session, sub_category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Sub Category not found")
