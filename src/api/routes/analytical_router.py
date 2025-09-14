from fastapi import APIRouter, Depends, status
from fastapi_cache.decorator import cache
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth.clerk import require_role
from src.api.di.db_helper import db_helper
from src.api.services.analytical_service import AnalyticalService
from src.schemas.analytical_schema import ProductFacetsSchema
from src.schemas.common.enums import Role
from src.schemas.product_schema import ProductAnalyticalSchema
from src.utils.cache_coder import ORJsonCoder

router = APIRouter(
    tags=["Analytics"],
    prefix="/analytics",
    dependencies=[Depends(require_role(Role.EMPLOYEE))],
)


@router.get(
    "/products/best-selling",
    response_model=list[ProductAnalyticalSchema],
    summary="Return best selling products",
    status_code=status.HTTP_200_OK,
)
@cache(60 * 60, coder=ORJsonCoder)
async def get_best_selling_products(
    db_session: AsyncSession = Depends(db_helper.session_getter),
):
    """
    Retrieves the best-selling products from the database and returns them as a list of dictionaries.
    """
    result_rows = await AnalyticalService.get_sold_products(db_session)
    return [
        ProductAnalyticalSchema(
            name=name,
            sold=sold,
            revenue=revenue,
            image_url=image_url,
        )
        for name, image_url, sold, revenue in result_rows
    ]


@router.get(
    "/products/facets",
    response_model=ProductFacetsSchema,
    summary="Return product facets",
    status_code=status.HTTP_200_OK,
)
@cache(60 * 60, coder=ORJsonCoder)
async def get_product_facets(
    db_session: AsyncSession = Depends(db_helper.session_getter),
):
    """
    Retrieves product facets including category and sub-category counts.
    """
    facets = await AnalyticalService.calculate_product_facets(db_session)
    return facets
