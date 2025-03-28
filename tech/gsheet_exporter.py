import uuid

import gspread
import pandas as pd
from loguru import logger
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from src.config.config import settings
from src.models.models import Category, Product, SubCategory

TABLE = "new_price_ford"
SHEET = "main"


def load_sheet_to_db():
    # --- Подключение к Google Sheets ---
    gc = gspread.service_account(filename="credentials/tcf-service-account.json")
    sh = gc.open(TABLE)
    worksheet = sh.worksheet(SHEET)
    data = worksheet.get_all_values()
    df = pd.DataFrame(data)

    logger.info(f"Загружено {len(df)-1} строк из Google Sheet")

    # --- Настроим колонки ---
    df.columns = df.iloc[0]  # первая строка = заголовки
    df = df.drop(0).reset_index(drop=True)

    # --- Подключение к БД ---
    engine = create_engine(settings.DB.PSQL_URL.replace("asyncpg", "psycopg2"))
    session = Session(engine)

    # --- Предзагрузка существующих категорий и подкатегорий ---
    existing_categories = {
        c.name: c for c in session.execute(select(Category)).scalars().all()
    }
    existing_subcategories = {
        (s.name, s.category_id): s
        for s in session.execute(select(SubCategory)).scalars().all()
    }

    products_to_insert = []

    for _, row in df.iterrows():
        try:
            category_name = row["category"]
            sub_category_name = row["sub_category"]

            # --- Категория ---
            category = existing_categories.get(category_name)
            if not category:
                category = Category(id=uuid.uuid4(), name=category_name)
                session.add(category)
                session.flush()
                existing_categories[category_name] = category

            # --- Подкатегория ---
            sub_category = existing_subcategories.get((sub_category_name, category.id))
            if not sub_category:
                sub_category = SubCategory(
                    id=uuid.uuid4(),
                    name=sub_category_name,
                    category_id=category.id,
                )
                session.add(sub_category)
                session.flush()
                existing_subcategories[(sub_category_name, category.id)] = sub_category

            # --- Товар ---
            def parse_price(value: str) -> float:
                return float(str(value).replace(",", ".").strip())

            product = Product(
                id=uuid.uuid4(),
                bitrix_id=row.get("bitrix_id") or None,
                address_id=row.get("address_id") or None,
                name=row["name"],
                brand=row["brand"],
                manufacturer_number=row.get("manufacturer_number") or None,
                cross_number=row.get("cross_number") or None,
                description=row.get("description") or None,
                image_url=row.get("image_url") or None,
                price_rub=parse_price(row["price_rub"]),
                super_wholesale_price_rub=parse_price(
                    row.get("super_wholesale_price_rub") or "0"
                ),
                quantity=int(row["quantity"]),
                sub_category_id=sub_category.id,
            )

            products_to_insert.append(product)

        except Exception as e:
            logger.error(f"Ошибка при обработке строки: {row.to_dict()}")
            logger.exception(e)

    logger.info(f"Готово к вставке: {len(products_to_insert)} товаров")
    session.bulk_save_objects(products_to_insert)
    session.commit()
    session.close()

    logger.success("Импорт завершён успешно!")


if __name__ == "__main__":
    load_sheet_to_db()
