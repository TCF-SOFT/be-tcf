from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

from schemas.enums import PriceListExt, PriceListType
from src.config import settings


async def serve_price(price_type: PriceListType, ext: PriceListExt = "csv") -> Path:
    """
    Serve a price list in the specified format (CSV or XLSX).
    If the file already exists, return its path.
    If not, generate the price list and return the new path.
    """
    file_name: str = (
        f"price_retail.{ext}"
        if price_type == PriceListType.RETIAL
        else f"price_wholesale.{ext}"
    )
    folder = Path("tmp/")
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / file_name

    if path.exists():
        return path
    else:
        return await generate_price(price_type, ext)


async def generate_price(price_type: PriceListType, ext: PriceListExt = "csv") -> Path:
    """
    Generate a price list in the specified format (CSV or XLSX).
    """
    query = text("""
    SELECT p.bitrix_id,
       c.name AS "Система",
       sc.name AS "Подсистема",
       p.name AS "Название",
       o.brand AS "Бренд",
       o.manufacturer_number AS "Номер производителя",
       p.cross_number AS "Кроссы",
       o.price_rub AS "Цена",
       (o.price_rub + o.super_wholesale_price_rub) / 2 AS "Цена опт",
       o.super_wholesale_price_rub AS "Цена супер-опт",
       o.quantity AS "Остаток"
    FROM categories c
         JOIN sub_categories sc ON c.id = sc.category_id
         JOIN products p ON sc.id = p.sub_category_id
         JOIN offers o on p.id = o.product_id;
    """)
    db_url = settings.DB.PSQL_URL.replace("asyncpg", "psycopg2")
    engine = create_engine(db_url)

    df = pd.read_sql_query(query, engine)

    # Version with SQLAlchemy ORM
    # offers_raw: list[OfferSchema] = await OfferDAO.find_all_base(db_session, {})
    # offers: list[OfferSchema] = [OfferSchema.model_validate(offer) for offer in offers_raw]
    # df = pd.DataFrame([offer.model_dump() for offer in offers])

    file_name: str = (
        f"price_retail.{ext}"
        if price_type == PriceListType.RETIAL
        else f"price_wholesale.{ext}"
    )
    folder = Path("tmp/")
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / file_name

    if ext == PriceListExt.EXCEL:
        df.to_excel(path, index=False, sheet_name="Прайс-лист", freeze_panes=(1, 0))
    else:
        df.to_csv(path, index=False)

    return path
