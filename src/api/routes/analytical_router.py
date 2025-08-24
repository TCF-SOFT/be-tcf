from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.di.db_helper import db_helper
from src.api.services.analytical_service import AnalyticalService
from src.schemas.product_schema import ProductAnalyticalSchema

router = APIRouter(tags=["Analytics"], prefix="/analytics")


@router.get(
    "/products/best-selling",
    response_model=list[ProductAnalyticalSchema],
    summary="Return best selling products",
    status_code=status.HTTP_200_OK,
)
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
