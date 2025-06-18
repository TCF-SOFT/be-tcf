import numpy as np
import pandas as pd
import psycopg2
from loguru import logger
from openai import OpenAI
from pgvector.psycopg2 import register_vector
from psycopg2.extras import execute_values
from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from src.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

# Разбор SQLAlchemy-style URL → psycopg2-совместимая строка
sqlalchemy_url = make_url(settings.DB.PSQL_URL)
psycopg2_dsn = (
    f"dbname={sqlalchemy_url.database} "
    f"user={sqlalchemy_url.username} "
    f"password={sqlalchemy_url.password} "
    f"host={sqlalchemy_url.host} "
    f"port={sqlalchemy_url.port}"
)

# SQLAlchemy engine для чтения
engine = create_engine(settings.DB.PSQL_URL.replace("asyncpg", "psycopg2"))


BATCH_SIZE = 100


def build_product_text(row):
    parts = [
        row["name"].strip(),
        f"Brand: {row['brand']}" if pd.notnull(row["brand"]) else "",
        f"Manufacturer Number: {row['manufacturer_number']}"
        if pd.notnull(row["manufacturer_number"])
        else "",
        f"Cross Number: {row['cross_number']}"
        if pd.notnull(row["cross_number"])
        else "",
        f"Category: {row['sub_category_slug']}"
        if pd.notnull(row["sub_category_slug"])
        else "",
    ]
    return " | ".join([p for p in parts if p])


def embed_batch(texts: list[str]):
    try:
        response = client.embeddings.create(input=texts, model="text-embedding-3-small")
        return [r.embedding for r in response.data]
    except Exception as e:
        logger.error(f"OpenAI embedding error: {e}")
        return [None] * len(texts)


def bulk_update_embeddings(data):
    with psycopg2.connect(psycopg2_dsn) as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            logger.info(f"⬆️ Обновляем {len(data)} записей в базе...")
            execute_values(
                cur,
                """
                UPDATE products AS p
                SET embedding = data.embedding::vector
                FROM (VALUES %s) AS data(id, embedding)
                WHERE p.id = data.id
                """,
                data,
                template="(%s, %s)",
            )
            conn.commit()


def main():
    logger.info("🚀 Загружаем товары из базы...")
    with engine.connect() as conn:
        df = pd.read_sql(
            """
            SELECT id, name, manufacturer_number, brand, cross_number, sub_category_slug
            FROM products
            WHERE name IS NOT NULL
            ORDER BY id
        """,
            conn,
        )

    logger.info(f"🔢 Загружено товаров: {len(df)}")
    df["text"] = df.apply(build_product_text, axis=1)

    all_embeddings = []
    logger.info("💡 Генерация embedding'ов батчами...")
    for start in range(0, len(df), BATCH_SIZE):
        end = start + BATCH_SIZE
        batch = df.iloc[start:end]
        texts = batch["text"].tolist()
        ids = batch["id"].tolist()

        logger.info(f"🧠 Обрабатываем {start}–{min(end, len(df))} из {len(df)}...")
        embeddings = embed_batch(texts)

        valid_rows = [
            (id_, np.array(embedding))
            for id_, embedding in zip(ids, embeddings)
            if embedding
        ]
        if valid_rows:
            bulk_update_embeddings(valid_rows)
        else:
            logger.warning(f"⚠️ Не удалось получить embedding для {len(texts)} строк.")

        all_embeddings.extend(valid_rows)

    logger.info(f"📦 Всего embedding'ов получено: {len(all_embeddings)}")

    logger.success("✅ Обработка завершена!")


if __name__ == "__main__":
    main()
