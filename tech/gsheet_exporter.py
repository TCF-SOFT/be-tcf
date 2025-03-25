import uuid

import gspread
import pandas as pd
from loguru import logger
from sqlalchemy import create_engine

from src.config.config import settings

TABLE = "new_price_ford"
SHEET = "main"

# --- Setup Logging ---
logger.info("Starting the Google Sheets to Postgres pipeline")

try:
    # --- Authenticate and Access Google Sheet ---
    gc = gspread.service_account(filename="credentials/tcf-service-account.json")
    sh = gc.open(TABLE)  # Replace with dynamic if needed
    worksheet = sh.worksheet(SHEET)  # Adjust as needed

    logger.info("Successfully connected to Google Sheet")

    # --- Load Sheet Data ---
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    logger.info(f"Loaded {len(df)} rows from Google Sheet")

    # --- Generate UUIDs for each row ---
    df["id"] = [str(uuid.uuid4()) for _ in range(len(df))]
    logger.debug("UUIDs added to each row")

    # --- Connect to PostgreSQL ---
    db_url = settings.DB.PSQL_URL.replace("asyncpg", "psycopg2")  # for SQLAlchemy sync
    engine = create_engine(db_url)
    logger.info("Connected to PostgreSQL")

    # --- Append to Table ---
    df.to_sql("products", engine, if_exists="append", index=False)
    logger.success("Data written to PostgreSQL (appended to table)")

except Exception as e:
    logger.exception(f"Pipeline failed: {e}")
