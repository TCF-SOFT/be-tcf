from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi_cache.decorator import cache
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.controllers.create_entity_controller import create_entity_with_image
from api.controllers.update_entity_controller import update_entity_with_optional_image
from api.dao.category_dao import CategoryDAO
from api.dao.sub_category_dao import SubCategoryDAO
from api.routes.fastapi_users_router import require_employee
from common.deps.s3_service import get_s3_service
from common.services.s3_service import S3Service
from schemas.category_schema import CategorySchema
from schemas.sub_category_schema import (
    SubCategoryPostSchema,
    SubCategoryPutSchema,
    SubCategorySchema,
)
from src.api.di.db_helper import db_helper
from utils.cache_coder import ORJsonCoder

router = APIRouter(tags=["Sub-Categories"], prefix="/sub-categories")


@router.get(
    "",
    response_model=list[SubCategorySchema] | None,
    summary="",
    status_code=status.HTTP_200_OK,
)
@cache(expire=60 * 10, coder=ORJsonCoder)
async def get_sub_categories(
    db_session: AsyncSession = Depends(db_helper.session_getter),
    category_id: UUID | None = None,
    category_slug: str = None,
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

    return await SubCategoryDAO.find_all(db_session, filter_by=filters)


@router.get(
    "/{slug}",
    response_model=SubCategorySchema | None,
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
    dependencies=[Depends(require_employee)],
)
async def post_sub_category(
    sub_category: SubCategoryPostSchema,
    image_blob: UploadFile = File(...),
    db_session: AsyncSession = Depends(db_helper.session_getter),
    s3: S3Service = Depends(get_s3_service),
):
    return await create_entity_with_image(
        payload=sub_category,
        image_blob=image_blob,
        upload_path="images/tmp",
        db_session=db_session,
        s3=s3,
        dao=SubCategoryDAO,
        refresh_fields=["category"],
    )


@router.put(
    "/{sub_category_id}",
    response_model=SubCategorySchema,
    summary="Update a sub_category by id",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_employee)],
)
async def put_sub_category(
    sub_category_id: UUID,
    sub_category: SubCategoryPutSchema,
    image_blob: UploadFile | None = File(None),
    db_session: AsyncSession = Depends(db_helper.session_getter),
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
    "/{sub_category_id}",
    summary="Delete sub_category by id",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_employee)],
)
async def delete_sub_category(
    sub_category_id: UUID,
    db_session: AsyncSession = Depends(db_helper.session_getter),
):
    success = await SubCategoryDAO.delete_by_id(db_session, sub_category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Sub Category not found")
