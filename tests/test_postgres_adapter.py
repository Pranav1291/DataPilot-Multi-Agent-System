
import pytest
from sqlalchemy import create_engine

from datapilot.connectors.models import QuerySpec
from datapilot.connectors.sql.postgres import PostgresAdapter


@pytest.fixture
def adapter():
    # No database connection is opened by create_engine itself.
    engine = create_engine("postgresql+psycopg://user:pass@localhost/test")
    instance = PostgresAdapter(engine)
    yield instance
    engine.dispose()


def test_accepts_select_query(adapter):
    query = QuerySpec(
        language="sql",
        payload={"statement": "SELECT id, name FROM customers"},
    )

    assert adapter._validate_query(query) == (
        "SELECT id, name FROM customers"
    )


def test_rejects_update_query(adapter):
    query = QuerySpec(
        language="sql",
        payload={"statement": "UPDATE customers SET name = 'test'"},
    )

    with pytest.raises(ValueError, match="Only a single SELECT"):
        adapter._validate_query(query)


def test_rejects_multiple_statements(adapter):
    query = QuerySpec(
        language="sql",
        payload={"statement": "SELECT 1; SELECT 2"},
    )

    with pytest.raises(ValueError, match="Only a single SELECT"):
        adapter._validate_query(query)


def test_rejects_select_into(adapter):
    query = QuerySpec(
        language="sql",
        payload={"statement": "SELECT id INTO new_table FROM customers"},
    )

    with pytest.raises(ValueError, match="SELECT INTO"):
        adapter._validate_query(query)


def test_rejects_non_sql_query(adapter):
    query = QuerySpec(
        language="mongodb_find",
        payload={"collection": "customers"},
    )

    with pytest.raises(ValueError, match="requires an SQL"):
        adapter._validate_query(query)


def test_rejects_write_inside_cte(adapter):
    query = QuerySpec(
        language="sql",
        payload={
            "statement": (
                "WITH changed AS ("
                "UPDATE customers SET name = 'test' RETURNING id"
                ") SELECT * FROM changed"
            )
        },
    )

    with pytest.raises(
        ValueError, match="read-only SELECT operations"
    ):
        adapter._validate_query(query)


def test_rejects_select_for_update(adapter):
    query = QuerySpec(
        language="sql",
        payload={
            "statement": "SELECT * FROM customers FOR UPDATE"
        },
    )

    with pytest.raises(
        ValueError, match="read-only SELECT operations"
    ):
        adapter._validate_query(query)
