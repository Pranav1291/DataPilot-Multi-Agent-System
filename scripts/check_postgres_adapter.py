
from datapilot.connectors.models import QuerySpec
from datapilot.connectors.sql.connection import (
    get_postgres_adapter,
    get_postgres_engine,
)


def main() -> None:
    adapter = get_postgres_adapter()

    try:
        # Discover tables and columns without manually defining a schema.
        metadata = adapter.get_metadata()
        print("Discovered database:", metadata.database_name)

        for resource in metadata.resources:
            print(f"\n{resource.resource_type}: {resource.name}")
            for field in resource.fields:
                print(f"  - {field.name}: {field.data_type}")

        # Execute a read-only query through the adapter.
        query = QuerySpec(
            language="sql",
            payload={
                "statement": (
                    "SELECT id, name, city, revenue "
                    "FROM customers ORDER BY id"
                )
            },
            limit=100,
        )

        result = adapter.execute_readonly(query)

        print("\nQuery results:")
        for row in result.rows:
            print(row)

        print("\nRows returned:", result.row_count)
        print("Results truncated:", result.truncated)
        print(f"Execution time: {result.execution_time_ms:.2f} ms")

    finally:
        # Close the pool after this standalone diagnostic script.
        get_postgres_engine().dispose()
        get_postgres_engine.cache_clear()


if __name__ == "__main__":
    main()
