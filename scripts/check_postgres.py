
from sqlalchemy import text

from datapilot.connectors.sql.connection import (
    get_postgres_engine,
)


def main() -> None:
    """Verify that DataPilot can connect to PostgreSQL."""
    engine = get_postgres_engine()

    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT current_database(), current_user")
            )
            database, user = result.one()

        print(f"Connected to database: {database}")
        print(f"Connected as user: {user}")
    finally:
        # Release the connection pool when the test finishes.
        engine.dispose()
        get_postgres_engine.cache_clear()


if __name__ == "__main__":
    main()
