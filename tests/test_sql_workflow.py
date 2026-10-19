from unittest.mock import MagicMock

from datapilot.agents import sql_workflow
from datapilot.agents.sql_generator import SQLGeneration
from datapilot.connectors.models import (
    DatabaseMetadata,
    FieldMetadata,
    QueryResult,
    ResourceMetadata,
)
from datapilot.connectors.sql.postgres import PostgresAdapter


def test_workflow_runs_all_three_nodes(monkeypatch):
    metadata = DatabaseMetadata(
        source_type="postgresql",
        database_name="datapilot",
        resources=[
            ResourceMetadata(
                name="customers",
                resource_type="table",
                fields=[
                    FieldMetadata(name="city", data_type="VARCHAR"),
                    FieldMetadata(name="revenue", data_type="NUMERIC"),
                ],
            )
        ],
    )

    expected_sql = (
        "SELECT city, SUM(revenue) AS total_revenue "
        "FROM customers GROUP BY city"
    )

    adapter = MagicMock(spec=PostgresAdapter)
    adapter.get_metadata.return_value = metadata
    adapter.execute_readonly.return_value = QueryResult(
        columns=["city", "total_revenue"],
        rows=[
            {"city": "Delhi", "total_revenue": 282500.00},
            {"city": "Mumbai", "total_revenue": 98000.00},
        ],
        row_count=2,
        truncated=False,
        execution_time_ms=5.0,
    )

    monkeypatch.setattr(
        sql_workflow,
        "generate_sql",
        lambda question, metadata: SQLGeneration(
            sql_statement=expected_sql,
            explanation="Calculates revenue grouped by city.",
        ),
    )

    graph = sql_workflow.build_sql_workflow(adapter)
    output = graph.invoke(
        {"question": "What is the total revenue by city?"}
    )

    adapter.get_metadata.assert_called_once()
    adapter.execute_readonly.assert_called_once()

    assert output["sql_statement"] == expected_sql
    assert output["result"].row_count == 2
    assert output["result"].rows[0]["city"] == "Delhi"