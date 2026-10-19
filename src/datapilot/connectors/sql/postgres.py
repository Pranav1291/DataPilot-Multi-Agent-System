
from time import perf_counter
from typing import Any

import sqlglot
from sqlalchemy import Engine, inspect, text
from sqlglot import exp

from datapilot.connectors.models import (
    DatabaseMetadata,
    FieldMetadata,
    QueryResult,
    QuerySpec,
    ResourceMetadata,
)


class PostgresAdapter:
    """Execute validated, read-only queries against PostgreSQL."""

    def __init__(
        self,
        engine: Engine,
        schema: str = "public",
        statement_timeout_ms: int = 5000,
    ) -> None:
        if not 1 <= statement_timeout_ms <= 120_000:
            raise ValueError("Statement timeout must be 1–120000 ms.")

        self.engine = engine
        self.schema = schema
        self.statement_timeout_ms = statement_timeout_ms

    @property
    def source_type(self) -> str:
        return "postgresql"

    def get_metadata(self) -> DatabaseMetadata:
        """Discover tables, views, and their columns."""
        inspector = inspect(self.engine)
        resources: list[ResourceMetadata] = []

        tables = inspector.get_table_names(schema=self.schema)
        views = inspector.get_view_names(schema=self.schema)

        for name, resource_type in [
            *((table, "table") for table in tables),
            *((view, "view") for view in views),
        ]:
            fields = [
                FieldMetadata(
                    name=column["name"],
                    data_type=str(column["type"]),
                    nullable=column.get("nullable"),
                )
                for column in inspector.get_columns(
                    name, schema=self.schema
                )
            ]

            resources.append(
                ResourceMetadata(
                    name=name,
                    resource_type=resource_type,
                    fields=fields,
                )
            )

        return DatabaseMetadata(
            source_type="postgresql",
            database_name=self.engine.url.database,
            resources=resources,
        )

    @staticmethod
    def _validate_query(query: QuerySpec) -> str:
        """Allow one SELECT statement and reject other SQL operations."""
        if query.language != "sql":
            raise ValueError("PostgreSQL requires an SQL query.")

        statement = query.payload.get("statement")
        if not isinstance(statement, str) or not statement.strip():
            raise ValueError("A non-empty SQL statement is required.")

        try:
            parsed = sqlglot.parse(statement, read="postgres")
        except sqlglot.errors.ParseError as exc:
            raise ValueError("Invalid PostgreSQL query syntax.") from exc

        # Reject multiple statements and anything other than SELECT.
        if (
            len(parsed) != 1
            or parsed[0] is None
            or not isinstance(parsed[0], exp.Select)
        ):
            raise ValueError("Only a single SELECT query is allowed.")

        # SELECT INTO can create a table, so it is not allowed.
        if parsed[0].args.get("into") is not None:
            raise ValueError("SELECT INTO is not allowed.")
        
        # Inspect the entire syntax tree, including nested CTE statements.
        # A top-level SELECT must not hide a write or locking operation.
        forbidden_operations = {
            "insert",
            "update",
            "delete",
            "merge",
            "create",
            "drop",
            "alter",
            "truncate",
            "copy",
            "command",
            "grant",
            "revoke",
            "lock",
        }

        for node in parsed[0].walk():
            if node.key.lower() in forbidden_operations:
                raise ValueError(
                    "Only read-only SELECT operations are allowed."
                )


        return statement.strip().rstrip(";")

    def execute_readonly(self, query: QuerySpec) -> QueryResult:
        """Run a query inside a read-only transaction with limits."""
        statement = self._validate_query(query)
        limit = query.limit

        params: dict[str, Any] = dict(query.parameters)
        if "_datapilot_limit" in params:
            raise ValueError("Reserved query parameter name.")

        # The outer limit also bounds queries without their own LIMIT.
        bounded_sql = (
            f"SELECT * FROM ({statement}) AS datapilot_result "
            "LIMIT :_datapilot_limit"
        )
        params["_datapilot_limit"] = limit + 1

        started = perf_counter()

        with self.engine.connect() as connection, connection.begin():
            # These settings apply only to this transaction.
            connection.exec_driver_sql("SET TRANSACTION READ ONLY")
            connection.exec_driver_sql(
                f"SET LOCAL statement_timeout = "
                f"{self.statement_timeout_ms}"
            )

            result = connection.execute(text(bounded_sql), params)
            columns = list(result.keys())
            fetched = result.mappings().fetchmany(limit + 1)

        truncated = len(fetched) > limit
        rows = [dict(row) for row in fetched[:limit]]

        return QueryResult(
            columns=columns,
            rows=rows,
            row_count=len(rows),
            truncated=truncated,
            execution_time_ms=(perf_counter() - started) * 1000,
        )
