import asyncio

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

from src.api.models.drinks import (  # noqa
    Cart,  # noqa
    CartItem,  # noqa
    Cocktail,  # noqa
    CocktailLabel,  # noqa
    Image,  # noqa
    Label,  # noqa
    Order,  # noqa
    OrderCocktail,  # noqa
    User,  # noqa
)  # noqa
from src.config.config import settings
from src.models.base import Base

# TODO: read a guide how to define models in project (several files or just one) and metadata
target_metadata = Base.metadata


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
    connectable = create_async_engine(settings.db.PSQL_URL, future=True)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


asyncio.run(run_migrations_online())
