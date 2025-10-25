from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.analytical_schema import (
    CategoryFacet,
    ProductFacetsSchema,
    SubCategoryFacet,
)
from src.models import Category, Offer, Product, SubCategory, Waybill, WaybillOffer
from src.schemas.common.enums import WaybillType


class AnalyticalService:
    @staticmethod
    async def get_sold_products(session: AsyncSession):
        """
        SELECT
           p.name,
           p.image_url,
           SUM(waybill_offers.quantity) AS sold,
           SUM(waybill_offers.quantity * waybill_offers.price_rub) AS revenue
        FROM waybills
            JOIN waybill_offers ON waybills.id = waybill_offers.waybill_id
            JOIN offers o ON waybill_offers.offer_id = o.id
            JOIN products p ON o.product_id = p.id
        WHERE waybills.is_pending = false and waybills.waybill_type = 'WAYBILL_OUT'
        GROUP BY p.name
        ORDER BY sold DESC;
        """
        query = (
            select(
                Product.name,
                Product.image_url,
                func.sum(WaybillOffer.quantity).label("sold"),
                func.sum(WaybillOffer.quantity * WaybillOffer.price_rub).label(
                    "revenue"
                ),
            )
            .join(Offer, Offer.id == WaybillOffer.offer_id)
            .join(Product, Product.id == Offer.product_id)
            .join(Waybill, Waybill.id == WaybillOffer.waybill_id)
            .where(~Waybill.is_pending, Waybill.waybill_type == WaybillType.WAYBILL_OUT)
            .group_by(Product.name, Product.image_url)
            .order_by(func.sum(WaybillOffer.quantity).desc())
        )

        result = await session.execute(query)
        rows = result.all()

        return rows

    @staticmethod
    async def calculate_product_facets(session: AsyncSession) -> ProductFacetsSchema:
        # Category facets
        q1 = (
            select(Category.slug, func.count(Product.id).label("product_count"))
            .join(SubCategory, SubCategory.category_id == Category.id)
            .join(Product, Product.sub_category_id == SubCategory.id)
            .group_by(Category.slug)
        )
        res1 = await session.execute(q1)
        categories = [
            CategoryFacet(category_slug=slug, product_count=cnt)
            for slug, cnt in res1.all()
        ]

        # SubCategory facets
        q2 = (
            select(SubCategory.slug, func.count(Product.id).label("product_count"))
            .join(Product, Product.sub_category_id == SubCategory.id)
            .group_by(SubCategory.slug)
        )
        res2 = await session.execute(q2)
        sub_categories = [
            SubCategoryFacet(sub_category_slug=slug, product_count=cnt)
            for slug, cnt in res2.all()
        ]

        return ProductFacetsSchema(categories=categories, sub_categories=sub_categories)
