import asyncio

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine
from src.config import settings




from src.models import Base
from src.utils.logging import logger

# ? use `__init__.py` in `models` to import all models
target_metadata = Base.metadata

logger.info("Tables seen by Alembic:")
for t in Base.metadata.tables:
    logger.info("%r", t)

def do_run_migrations(connection):
    context.configure(
        compare_type=True,
        dialect_opts={"paramstyle": "named"},
        connection=connection,
        target_metadata=target_metadata,
        include_schemas=True,
        # literal_binds=True,
        version_table_schema=target_metadata.schema,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = create_async_engine(settings.DB.PSQL_URL, future=True)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


asyncio.run(run_migrations_online())
