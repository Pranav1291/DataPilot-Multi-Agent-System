
from typing import Protocol

from datapilot.connectors.models import (
    DatabaseMetadata,
    DatabaseType,
    QueryResult,
    QuerySpec,
)


class DatabaseAdapter(Protocol):
    """Contract that every database connector must implement."""

    @property
    def source_type(self) -> DatabaseType:
        """Identify the database technology."""
        ...

    def get_metadata(self) -> DatabaseMetadata:
        """Return the discoverable database structure."""
        ...

    def execute_readonly(self, query: QuerySpec) -> QueryResult:
        """Execute a validated, read-only query plan."""
        ...
