
from unittest.mock import MagicMock

import pytest

from datapilot.agents import sql_generator
from datapilot.agents.sql_generator import (
    SQLGeneration,
    format_schema,
    generate_sql,
)
from datapilot.connectors.models import (
    DatabaseMetadata,
    FieldMetadata,
    ResourceMetadata,
)


@pytest.fixture
def metadata():
    return DatabaseMetadata(
        source_type="postgresql",
        database_name="datapilot",
        resources=[
            ResourceMetadata(
                name="customers",
                resource_type="table",
                fields=[
                    FieldMetadata(name="id", data_type="INTEGER"),
                    FieldMetadata(name="city", data_type="VARCHAR"),
                    FieldMetadata(name="revenue", data_type="NUMERIC"),
                ],
            )
        ],
    )


def test_format_schema_includes_columns(metadata):
    schema = format_schema(metadata)

    assert "customers" in schema
    assert "city: VARCHAR" in schema
    assert "revenue: NUMERIC" in schema


def test_rejects_empty_question(metadata):
    with pytest.raises(ValueError, match="cannot be empty"):
        generate_sql("   ", metadata)


def test_rejects_unsupported_database():
    metadata = DatabaseMetadata(
        source_type="mongodb",
        database_name="datapilot",
    )

    with pytest.raises(ValueError, match="PostgreSQL only"):
        generate_sql("Count customers", metadata)


def test_generates_and_validates_sql(metadata, monkeypatch):
    expected = SQLGeneration(
        sql_statement=(
            "SELECT city, SUM(revenue) AS total_revenue "
            "FROM customers GROUP BY city"
        ),
        explanation="Calculates total revenue for each city.",
    )

    structured_llm = MagicMock()
    structured_llm.invoke.return_value = expected

    llm = MagicMock()
    llm.with_structured_output.return_value = structured_llm

    monkeypatch.setattr(
        sql_generator, "get_llm", lambda: llm
    )

    result = generate_sql(
        "What is the total revenue by city?",
        metadata,
    )

    assert result.sql_statement == expected.sql_statement
    assert result.explanation == expected.explanation
    structured_llm.invoke.assert_called_once()


def test_rejects_unsafe_generated_sql(metadata, monkeypatch):
    structured_llm = MagicMock()
    structured_llm.invoke.return_value = SQLGeneration(
        sql_statement="DELETE FROM customers",
        explanation="Delete customers.",
    )

    llm = MagicMock()
    llm.with_structured_output.return_value = structured_llm

    monkeypatch.setattr(
        sql_generator, "get_llm", lambda: llm
    )

    with pytest.raises(ValueError, match="Only a single SELECT"):
        generate_sql("Remove customers", metadata)
