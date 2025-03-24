import sys

import gspread
import pandas as pd
import uuid
from sqlalchemy import create_engine
from loguru import logger

from src.config.config import settings


TABLE = "price_all"
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
    df['id'] = [str(uuid.uuid4()) for _ in range(len(df))]
    logger.debug("UUIDs added to each row")

    sys.exit(0)
    # --- Connect to PostgreSQL ---
    db_url = settings.DB.PSQL_URL.replace("asyncpg", "psycopg2")  # for SQLAlchemy sync
    engine = create_engine(db_url)
    logger.info("Connected to PostgreSQL")

    # --- Overwrite Table ---
    df.to_sql("your_table_name", engine, if_exists='replace', index=False)
    logger.success("Data written to PostgreSQL (overwritten)")

except Exception as e:
    logger.exception(f"Pipeline failed: {e}")
