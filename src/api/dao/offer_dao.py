from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.api.dao.base import BaseDAO
from src.config import settings
from src.models import Offer, Product
from src.schemas.offer_schema import OfferSchema
from src.utils.pagination import Page


class OfferDAO(BaseDAO):
    model = Offer
    schema = OfferSchema

    @classmethod
    async def wildcard_search(
        cls,
        db_session: AsyncSession,
        search_term: str,
    ) -> Page[OfferSchema]:
        search_term = f"%{search_term}%"
        o = cls.model
        p = Product

        query = (
            select(o)
            .join(p, o.product_id == p.id)
            .where(
                or_(
                    func.lower(p.name).ilike(search_term),
                    func.lower(p.cross_number).ilike(search_term),
                    func.lower(o.manufacturer_number).ilike(search_term),
                    func.lower(o.brand).ilike(search_term),
                )
            )
            .options(joinedload(o.product))  # чтобы продукт был доступен
        )

        return await paginate(db_session, query)

    @classmethod
    async def full_text_search(
        cls,
        db_session,
        search_term: str,
    ) -> Page[OfferSchema]:
        """
        Perform a full-text search across product name, cross_number,
        offer brand and manufacturer_number using trigram similarity.
        """
        o = cls.model
        p = Product

        similarity_threshold = 0.15

        query = (
            select(o)
            .join(p, o.product_id == p.id)
            .where(
                or_(
                    func.similarity(p.name, search_term) > similarity_threshold,
                    func.similarity(p.cross_number, search_term) > similarity_threshold,
                    func.similarity(o.brand, search_term) > similarity_threshold,
                    func.similarity(o.manufacturer_number, search_term)
                    > similarity_threshold,
                )
            )
            .order_by(
                func.greatest(
                    func.similarity(o.brand, search_term),
                    func.similarity(p.name, search_term),
                    func.similarity(p.cross_number, search_term),
                    func.similarity(o.manufacturer_number, search_term),
                ).desc(),
                o.id.desc(),  # Ensure consistent ordering - no duplicates in Pagination
            )
        )
        return await paginate(db_session, query)

    @classmethod
    async def count_all(cls, db_session, filter_by: dict) -> dict[str, int]:
        """
        Count all objects in the database
        :param db_session:
        :param filter_by:
        :return:
        """
        query = select(func.count()).select_from(cls.model)

        filters = []

        if filter_by.get("product_id"):
            filters.append(cls.model.product_id == filter_by["product_id"])

        if filter_by.get("in_stock"):
            filters.append(cls.model.quantity > 0)

        if filter_by.get("is_image"):
            query = query.join(Product, cls.model.product)
            # filters.append(Product.image_url.isnot(None))
            filters.append(Product.image_url != settings.IMAGE_PLACEHOLDER_URL)
        elif filter_by.get("is_image") is False:
            query = query.join(Product, cls.model.product)
            filters.append(Product.image_url == settings.IMAGE_PLACEHOLDER_URL)
            # filters.append(Product.image_url.is_(None))

        query = query.where(and_(*filters))

        result = await db_session.execute(query)
        count = result.scalar_one()
        return {"count": count}
