import asyncio

import pandas as pd
from loguru import logger
from openai import AsyncClient
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from src.config import settings

client = AsyncClient(api_key=settings.OPENAI_API_KEY)

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

# Template
PROMPT_TEMPLATE = """
# Generate a description for auto spare part
## Task
Create a professional, engaging vehicle spare part (primary Ford) advertisement in Russian for ford-parts.com.ru
based on the provided vehicle spare part information.
The text should be 5-35 words long and focus on the spare part and where it probably used in car.
## Structure
1. **Spare part Overview**: Brief description of the spare part, its function, and its importance
2. **Ideal Usage**: Brief description of typical use cases and scenarios
## Style Guidelines
- Use natural, flowing paragraphs that incorporate features organically
- Create engaging descriptions that highlight practical benefits
- Translate spare parts names to Russian where appropriate (industry standard terms can remain)
- Describe equipment in terms of user benefits and real-world applications
- Vary your opening approaches - NEVER start with "Найдите" or "Откройте" or "Ищете", consider starting with driving
experience, spare part importance and reliability or standout feature
- Use diverse sentence structures and paragraph organization
## Important Restrictions
- Never mention:
  * Used/second-hand status
  * Warranties or guarantees
  * Vehicle condition statements
  * Availability timing
  * Original seller or dealership information
  * Pre-sale services
- Avoid:
  * Markdown formatting
  * Bullet points or feature lists
  * Basic/standard feature mentions without context
  * Phrases implying newness
  * Superlatives and unverifiable claims
  * Technical jargon without explanation
  * Inappropriate translations or double meanings

## Input data context:
1. Title is the name of the spare part. (if name doesn't make, e.g "1" - ignore it and try to use a cross_number
instead.)
2. Cross number is a unique identifier for the spare part.
3. Subcategory is given in English but it is a transliteration of Russian word.
4. id is the unique identifier (UUID) of the spare part in the internal database, always ignore it.

## Output
Response should be a string the generated description of the spare part.

## Input Data
Title: {name}
Cross Number: {cross_number}
Subcategory: {sub_category_slug}
"""


class ResponseModel(BaseModel):
    id: str
    description: str


def build_prompt(row) -> str:
    """
    Build a prompt for OpenAI API from a row of product data.
    """
    return PROMPT_TEMPLATE.format(
        name=row["name"],
        cross_number=row["cross_number"],
        sub_category_slug=row["sub_category_slug"],
        id=row["id"],
    )


async def generate_description(row) -> str | None:
    """
    Generate a description for a product using OpenAI API.
    """
    prompt = build_prompt(row)
    try:
        response = await client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        return None


async def main():
    logger.info("🔢 Загружаем товары из базы...")
    with engine.connect() as conn:
        df = pd.read_sql(
            """
            SELECT id, name, cross_number, sub_category_slug
            FROM products
            WHERE name IS NOT NULL
        """,
            conn,
        ).head(100)

    logger.info(f"🔢 Загружено товаров: {len(df)}")
    df["description"] = await asyncio.gather(
        *[generate_description(row) for _, row in df.iterrows()]
    )
    print(df.head())
    df.to_csv("generated_descriptions.csv", index=False)


if __name__ == "__main__":
    asyncio.run(main())
