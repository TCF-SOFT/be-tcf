from io import BytesIO
from typing import Literal
import pandas as pd
from sqlalchemy import create_engine, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.dao.offer_dao import OfferDAO
from api.dao.product_dao import ProductDAO
from config.config import settings
from models.models import Product
from schemas.offer_schema import OfferSchema
from schemas.product_schema import ProductSchema


async def generate_price(
    price_type: Literal["retail", "wholesale"], db_session: AsyncSession
) -> BytesIO:
    # Version with asyncpg raw query
    # query = query("""
    # SELECT p.id, p.name, o.price_rub, o.quantity
    # FROM products p
    # LEFT JOIN offers o ON p.id = o.product_id
    # """)
    # res = await db_session.execute(query)
    # print(res)

    # Version with SQLAlchemy ORM
    offers_raw: list[OfferSchema] = await OfferDAO.find_all_base(db_session, {})
    offers: list[OfferSchema] = [OfferSchema.model_validate(offer) for offer in offers_raw]
    df = pd.DataFrame([offer.model_dump() for offer in offers])
    return df.to_csv

    # Version with Pandas and psycopg2
    # db_url = settings.DB.PSQL_URL.replace("asyncpg", "psycopg2")
    # engine = create_engine(db_url)
    # products = pd.read_sql_table(
    #     "products", engine, columns=["id", "name"]
    # )
    # offers = pd.read_sql_table(
    #     "offers", engine, columns=["product_id", "price_rub", "quantity"]
    # )
    # join products and offers
    # df = pd.merge(products, offers, left_on="id", right_on="product_id", how="left")
    # print(df.head())
