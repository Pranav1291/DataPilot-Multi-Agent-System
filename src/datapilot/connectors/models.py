
from typing import Any, Literal

from pydantic import BaseModel, Field

DatabaseType = Literal[
    "postgresql",
    "mysql",
    "sqlserver",
    "mongodb",
    "elasticsearch",
]


class FieldMetadata(BaseModel):
    """Describe one field or column in a database resource."""

    name: str
    data_type: str
    nullable: bool | None = None


class ResourceMetadata(BaseModel):
    """Describe a table, view, collection, or index."""

    name: str
    resource_type: Literal["table", "view", "collection", "index"]
    fields: list[FieldMetadata] = Field(default_factory=list)


class DatabaseMetadata(BaseModel):
    """Describe the discoverable structure of a data source."""

    source_type: DatabaseType
    database_name: str | None = None
    resources: list[ResourceMetadata] = Field(default_factory=list)


class QuerySpec(BaseModel):
    """Represent a database-specific, read-only query plan."""

    language: Literal[
        "sql",
        "mongodb_find",
        "elasticsearch_dsl",
    ]
    payload: dict[str, Any]
    parameters: dict[str, Any] = Field(default_factory=dict)
    limit: int = Field(default=100, ge=1, le=1000)


class QueryResult(BaseModel):
    """Normalize query output across supported databases."""

    columns: list[str] = Field(default_factory=list)
    rows: list[dict[str, Any]] = Field(default_factory=list)
    row_count: int = Field(ge=0)
    truncated: bool = False
    execution_time_ms: float = Field(ge=0)
