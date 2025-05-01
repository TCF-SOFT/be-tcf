from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi_cache.decorator import cache
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.dao.sub_category_dao import SubCategoryDAO
from api.di.database import get_db
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
    slug: str = None,
    category_id: UUID | None = None,
    category_slug: str = None,
    count_only: bool = False,
):
    filters = {}
    if slug:
        filters["slug"] = slug
    if category_id:
        filters["category_id"] = category_id
    if category_slug:
        filters["category_slug"] = category_slug

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
async def create_sub_category(
    sub_category: SubCategoryPostSchema,
    db_session: AsyncSession = Depends(get_db),
):
    return await SubCategoryDAO.add(db_session, **sub_category.model_dump())


@router.put(
    "/sub-category/{sub_category_id}",
    response_model=int,
    summary="Update a sub_category by id",
    status_code=status.HTTP_200_OK,
)
async def put_sub_category(
    sub_category_id: UUID,
    category: SubCategoryPutSchema,
    db_session: AsyncSession = Depends(get_db),
):
    filters = {"id": sub_category_id}

    res: Annotated[int, "affected rows"] = await SubCategoryDAO.update(
        db_session, filters, **category.model_dump()
    )

    if not res:
        raise HTTPException(status_code=404, detail="Sub Category not found")
    return res


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
