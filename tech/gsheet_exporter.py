import gspread
import numpy as np
import pandas as pd
from loguru import logger
from sqlalchemy import create_engine

from src.config.config import settings

TABLE = "new_price_ford"
SHEETS = ["categories", "sub_categories", "products"]


# handle '' with None before export
def load_sheet_to_db():
    # --- Подключение к Google Sheets ---
    gc = gspread.service_account(filename="credentials/tcf-service-account.json")
    sh = gc.open(TABLE)

    # --- Подключение к БД (sync URL for SQLAlchemy engine) ---
    db_url = settings.DB.PSQL_URL.replace("asyncpg", "psycopg2")
    engine = create_engine(db_url)

    # --- Обработка каждого листа ---
    for sheet_name in SHEETS:
        worksheet = sh.worksheet(sheet_name)
        data = worksheet.get_all_values()

        df = pd.DataFrame(data)
        df.columns = df.iloc[0]  # первая строка — заголовки
        df = df.drop(0).reset_index(drop=True)
        df.replace(r"^\s*$", np.nan, regex=True, inplace=True)

        logger.info(f"📥 Загружено {len(df)} строк в таблицу {sheet_name}")
        df.to_sql(sheet_name, engine, if_exists="append", index=False)

    logger.success("✅ Импорт завершён успешно!")


if __name__ == "__main__":
    load_sheet_to_db()
