from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.api.dao.base import BaseDAO
from src.models import Offer, Product
from src.schemas.offer_schema import OfferSchema


class OfferDAO(BaseDAO):
    model = Offer

    @classmethod
    async def find_all_paginate(
        cls, db_session, filter_by: dict, order_by: str = None
    ) -> Page[OfferSchema]:
        query = select(cls.model).filter_by(**filter_by)
        return await paginate(db_session, query)

    @classmethod
    async def wildcard_search(
        cls,
        db_session,
        search_term: str,
    ) -> Page[OfferSchema]:
        search_term = f"%{search_term.replace('.', '')}%"

        query = select(cls.model).where(
            or_(
                func.replace(cls.model.brand, ".", "").ilike(search_term),
                func.replace(cls.model.manufacturer_number, ".", "").ilike(search_term),
            )
        )

        return await paginate(db_session, query)

    @classmethod
    async def smart_offer_search(
        cls, db_session: AsyncSession, search_term: str
    ) -> Page[OfferSchema]:
        search_term = f"%{search_term.lower()}%"
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

        similarity_threshold = 0.11

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
                    func.similarity(p.name, search_term),
                    func.similarity(p.cross_number, search_term),
                    func.similarity(o.brand, search_term),
                    func.similarity(o.manufacturer_number, search_term),
                ).desc(),
                o.id.desc(),  # Ensure consistent ordering - no duplicates in Pagination
            )
        )
        return await paginate(db_session, query)
