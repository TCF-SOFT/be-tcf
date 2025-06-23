from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.controllers.create_entity_controller import create_entity_with_image
from api.controllers.update_entity_controller import update_entity_with_optional_image
from api.dao.category_dao import CategoryDAO
from api.di.database import get_db
from api.routes.fastapi_users_router import require_employee
from common.deps.s3_service import get_s3_service
from common.services.s3_service import S3Service
from schemas.category_schema import (
    CategoryPostSchema,
    CategoryPutSchema,
    CategorySchema,
)

router = APIRouter(tags=["Categories"], prefix="/categories")


@router.get(
    "",
    response_model=list[CategorySchema],
    summary="Get all categories",
    status_code=status.HTTP_200_OK,
)
# @cache(expire=60 * 10, coder=ORJsonCoder)
async def get_categories(
    db_session: AsyncSession = Depends(get_db),
    order_by: str = None,
):
    return await CategoryDAO.find_all(db_session, filter_by={}, order_by=order_by)


@router.get(
    "/slug/{slug}",
    response_model=CategorySchema | None,
    summary="Get category by slug",
    status_code=status.HTTP_200_OK,
)
async def get_category_by_slug(
    slug: str,
    db_session: AsyncSession = Depends(get_db),
):
    return await CategoryDAO.find_by_slug(db_session, slug)


@router.get(
    "/{category_id}",
    response_model=CategorySchema | None,
    summary="Get category by id",
    status_code=status.HTTP_200_OK,
)
async def get_category_by_id(
    category_id: UUID,
    db_session: AsyncSession = Depends(get_db),
):
    return await CategoryDAO.find_by_id(db_session, category_id)


@router.post(
    "",
    response_model=CategorySchema,
    summary="Create a new category",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_employee)],
)
async def post_category(
    category_payload: CategoryPostSchema,
    image_blob: UploadFile = File(...),
    db_session: AsyncSession = Depends(get_db),
    s3: S3Service = Depends(get_s3_service),
):
    return await create_entity_with_image(
        payload=category_payload,
        image_blob=image_blob,
        upload_path="images/tmp",
        db_session=db_session,
        s3=s3,
        dao=CategoryDAO,
    )


@router.patch(
    "/{category_id}",
    response_model=CategorySchema,
    status_code=status.HTTP_200_OK,
    summary="Selective update category by id",
    dependencies=[Depends(require_employee)],
)
async def patch_category(
    category_id: UUID,
    category_payload: CategoryPutSchema,
    image_blob: UploadFile | None = File(None),
    db_session: AsyncSession = Depends(get_db),
    s3: S3Service = Depends(get_s3_service),
):
    return await update_entity_with_optional_image(
        entity_id=category_id,
        payload=category_payload,
        dao=CategoryDAO,
        upload_path="images/tmp",
        db_session=db_session,
        s3=s3,
        image_blob=image_blob,
    )


@router.delete(
    "/{category_id}",
    summary="Delete a category by id",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_employee)],
)
async def delete_category(
    category_id: UUID,
    db_session: AsyncSession = Depends(get_db),
):
    success = await CategoryDAO.delete_by_id(db_session, category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
