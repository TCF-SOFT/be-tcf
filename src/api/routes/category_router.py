from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.dao.category_dao import CategoryDAO
from api.di.database import get_db
from schemas.category_schema import (
    CategoryPostSchema,
    CategoryPutSchema,
    CategorySchema,
)

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
):
    return await CategoryDAO.add(db_session, **category.model_dump())


@router.put(
    "/category/{category_id}",
    response_model=int,
    summary="Update a category by id",
    status_code=status.HTTP_200_OK,
)
async def put_category(
    category_id: UUID,
    category: CategoryPutSchema,
    db_session: AsyncSession = Depends(get_db),
):
    filters = {"id": category_id}

    res: Annotated[int, "affected rows"] = await CategoryDAO.update(
        db_session, filters, **category.model_dump()
    )

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
