
from datapilot.agents.sql_workflow import build_sql_workflow
from datapilot.connectors.sql.connection import (
    get_postgres_adapter,
    get_postgres_engine,
)


def main() -> None:
    adapter = get_postgres_adapter()
    graph = build_sql_workflow(adapter)

    try:
        output = graph.invoke(
            {
                "question": "What is the revenue of DElhi?"
            }
        )

        print("\nGenerated SQL:")
        print(output["sql_statement"])

        print("\nExplanation:")
        print(output["explanation"])

        print("\nResults:")
        for row in output["result"].rows:
            print(row)

        print("\nRows returned:", output["result"].row_count)

    finally:
        get_postgres_engine().dispose()
        get_postgres_engine.cache_clear()


if __name__ == "__main__":
    main()
