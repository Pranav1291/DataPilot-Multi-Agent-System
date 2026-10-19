
from functools import lru_cache

from sqlalchemy import Engine, create_engine

from datapilot.config import get_settings
from datapilot.connectors.sql.postgres import PostgresAdapter


@lru_cache(maxsize=1)
def get_postgres_engine() -> Engine:
    """Create and reuse a PostgreSQL connection pool."""
    settings = get_settings()

    if not settings.postgres_url:
        raise ValueError(
            "PostgreSQL URL is missing. Configure "
            "DATAPILOT_POSTGRES_URL in your .env file."
        )

    return create_engine(
        settings.postgres_url.get_secret_value(),
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=5,
        pool_recycle=1800,
        hide_parameters=True,
    )


def get_postgres_adapter() -> PostgresAdapter:
    """Build the adapter using the shared connection pool."""
    return PostgresAdapter(engine=get_postgres_engine())
