
import pytest
from pydantic import ValidationError

from datapilot.connectors.models import (
    DatabaseMetadata,
    QueryResult,
    QuerySpec,
)


def test_database_metadata_supports_sql_and_nosql():
    # Both database families use the same metadata model.
    for source_type in ("postgresql", "mongodb", "elasticsearch"):
        metadata = DatabaseMetadata(
            source_type=source_type,
            resources=[],
        )
        assert metadata.source_type == source_type


def test_query_limit_is_bounded():
    query = QuerySpec(
        language="sql",
        payload={"statement": "SELECT 1"},
        limit=100,
    )
    assert query.limit == 100

    with pytest.raises(ValidationError):
        QuerySpec(
            language="sql",
            payload={"statement": "SELECT 1"},
            limit=5000,
        )


def test_query_result_has_a_common_shape():
    result = QueryResult(
        columns=["name"],
        rows=[{"name": "Alice"}],
        row_count=1,
        truncated=False,
        execution_time_ms=2.5,
    )

    assert result.row_count == 1
    assert result.rows[0]["name"] == "Alice"
